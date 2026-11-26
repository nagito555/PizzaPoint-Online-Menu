from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import database as db, authdb, secrets, re, os, smtplib
from email.message import EmailMessage
from functools import wraps
app=Flask(__name__);app.secret_key=os.getenv('FLASK_SECRET','techstore-demo-secret-change-me');app.config['SESSION_COOKIE_HTTPONLY']=True;app.config['SESSION_COOKIE_SAMESITE']='Lax'
db.initialize();authdb.initialize()
def user(): return authdb.user_by_id(session.get('user_id'))
@app.context_processor
def shared():
 u=user();return {'logged_user':u,'is_admin':bool(u and u['role']=='admin'),'cart_count':authdb.cart_count(u['id']) if u else 0}
def unpack(r):return {'id':r[0],'name':r[1],'category':r[2],'specs':r[3] or '', 'price':float(r[4] or 0),'stock':int(r[5] or 0),'image_url':r[6] or ''}
def login_required(f):
 @wraps(f)
 def w(*a,**kw):
  if not user():flash('Для продолжения войдите в аккаунт.','error');return redirect(url_for('login',next=request.path))
  return f(*a,**kw)
 return w
def admin_required(f):
 @wraps(f)
 def w(*a,**kw):
  u=user()
  if not u:flash('Войдите в аккаунт администратора.','error');return redirect(url_for('login'))
  if u['role']!='admin':flash('Эта функция доступна только администратору.','error');return redirect(url_for('index'))
  return f(*a,**kw)
 return w
def send_code(email,code):
 host=os.getenv('SMTP_HOST')
 if not host: print(f'\n[PizzaPoint DEV] Code for {email}: {code}\n');return False
 msg=EmailMessage();msg['Subject']='Код подтверждения PizzaPoint';msg['From']=os.getenv('SMTP_FROM',os.getenv('SMTP_USER'));msg['To']=email;msg.set_content(f'Ваш код подтверждения: {code}. Код действует 10 минут.')
 with smtplib.SMTP(host,int(os.getenv('SMTP_PORT','587'))) as s:s.starttls();s.login(os.getenv('SMTP_USER'),os.getenv('SMTP_PASSWORD'));s.send_message(msg)
 return True
def cart_products(uid):
 result=[]
 for x in authdb.cart_raw(uid):
  r=db.product_by_id(x['product_id'])
  if r:
   p=unpack(r);p['quantity']=x['quantity'];p['line_total']=p['price']*p['quantity'];result.append(p)
 return result
@app.route('/')
def index():
 q=request.args.get('q','').strip();cat=request.args.get('category','');items=[unpack(r) for r in db.products()]
 if q:items=[p for p in items if q.lower() in p['name'].lower() or q.lower() in p['specs'].lower()]
 if cat:items=[p for p in items if p['category']==cat]
 total,ncat,value=db.stats();return render_template('index.html',products=items,categories=db.categories(),search=q,selected_category=cat,total=total,category_count=ncat,value=value)
@app.route('/register',methods=['GET','POST'])
def register():
 if user():return redirect(url_for('profile'))
 if request.method=='POST':
  name=request.form.get('full_name','').strip();email=request.form.get('email','').strip().lower();phone=request.form.get('phone','').strip();pw=request.form.get('password','');confirm=request.form.get('confirm_password','')
  error=None
  if len(name.split())<2:error='Введите ФИО полностью (минимум имя и фамилия).'
  elif not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email):error='Некорректный адрес электронной почты.'
  elif not re.fullmatch(r'\+?\d[\d\s()\-]{9,17}',phone):error='Некорректный номер телефона.'
  elif len(pw)<8:error='Пароль должен содержать не менее 8 символов.'
  elif pw!=confirm:error='Пароли не совпадают.'
  elif authdb.user_by_email(email):error='Эта почта уже зарегистрирована.'
  if error:flash(error,'error')
  else:
   code=f'{secrets.randbelow(1000000):06d}';authdb.create_pending(name,email,phone,generate_password_hash(pw),code)
   try:
    sent=send_code(email,code);flash('Письмо с кодом отправлено.' if sent else 'Код выведен в консоль Python (SMTP не настроен).','success')
   except Exception as e:print(f'[PizzaPoint DEV] Verification code for {email}: {code}');flash('Письмо не отправилось; код выведен в консоль сервера.','error')
   return redirect(url_for('verify',email=email))
 return render_template('register.html')
@app.route('/verify',methods=['GET','POST'])
def verify():
 email=request.args.get('email','').lower()
 if request.method=='POST':email=request.form.get('email','').lower();code=request.form.get('code','').strip()
 if request.method=='POST':
  if authdb.verify(email,code):flash('Почта подтверждена! Теперь войдите.','success');return redirect(url_for('login'))
  flash('Код неверный или истёк (10 минут).','error')
 return render_template('verify.html',email=email)
@app.route('/login',methods=['GET','POST'])
def login():
 if user():return redirect(url_for('profile'))
 if request.method=='POST':
  email=request.form.get('email','').lower().strip();pw=request.form.get('password','');u=authdb.user_by_email(email)
  if u and u['verified'] and check_password_hash(u['password_hash'],pw):session.clear();session['user_id']=u['id'];flash('Вход выполнен.','success');dest=request.args.get('next','');return redirect(dest if dest.startswith('/') and not dest.startswith('//') else url_for('profile'))
  flash('Неверные данные или почта не подтверждена.','error')
 return render_template('login.html')
@app.route('/logout',methods=['POST'])
def logout():session.clear();flash('Вы вышли из аккаунта.','success');return redirect(url_for('index'))
@app.route('/profile')
@login_required
def profile():
 items=cart_products(user()['id']);return render_template('profile.html',user=user(),items=items,total=sum(p['line_total'] for p in items))
@app.route('/cart')
@login_required
def cart():
 items=cart_products(user()['id']);return render_template('cart.html',items=items,total=sum(p['line_total'] for p in items))
@app.route('/cart/add/<int:pid>',methods=['POST'])
@login_required
def add_cart(pid):
 r=db.product_by_id(pid)
 if r and unpack(r)['stock']>0:authdb.add_cart(user()['id'],pid);flash('Добавлено в корзину.','success')
 else:flash('Товар отсутствует или не найден.','error')
 return redirect(request.referrer or url_for('index'))
@app.route('/cart/update/<int:pid>',methods=['POST'])
@login_required
def update_cart(pid):
 try:q=int(request.form.get('quantity',1))
 except:q=1
 authdb.set_quantity(user()['id'],pid,q);return redirect(url_for('cart'))
@app.route('/cart/remove/<int:pid>',methods=['POST'])
@login_required
def remove_cart(pid):authdb.remove_cart(user()['id'],pid);flash('Удалено из корзины.','success');return redirect(url_for('cart'))
@app.route('/add',methods=['GET','POST'])
@admin_required
def add_product():
 if request.method=='POST':
  name=request.form.get('name','').strip();category=request.form.get('category','').strip();specs=request.form.get('specs','').strip();image=request.form.get('image_url','').strip()
  try:price=float(request.form.get('price',0));stock=int(request.form.get('stock',0))
  except:flash('Цена и количество должны быть числами.','error');return render_template('add_product.html')
  if not name or not category or price<0 or stock<0:flash('Проверь поля формы.','error');return render_template('add_product.html')
  t=db.table_name();c=db.column_names();db.execute(f'INSERT INTO {t} ({c[1]}, {c[2]}, {c[3]}, {c[4]}, {c[5]}, {c[6]}) VALUES (?, ?, ?, ?, ?, ?)',(name,category,specs,price,stock,image));flash('Товар добавлен.','success');return redirect(url_for('index'))
 return render_template('add_product.html')
@app.route('/edit/<int:pid>',methods=['GET','POST'])
@admin_required
def edit_product(pid):
 r=db.product_by_id(pid)
 if not r:flash('Не найден.','error');return redirect(url_for('index'))
 p=unpack(r)
 if request.method=='POST':
  p.update(name=request.form.get('name','').strip(),category=request.form.get('category','').strip(),specs=request.form.get('specs','').strip(),image_url=request.form.get('image_url','').strip())
  try:p['price']=float(request.form.get('price',0));p['stock']=int(request.form.get('stock',0))
  except:flash('Цена/остаток должны быть числами.','error');return render_template('edit_product.html',product=p)
  if not p['name'] or not p['category'] or p['price']<0 or p['stock']<0:flash('Проверь поля.','error');return render_template('edit_product.html',product=p)
  t=db.table_name();c=db.column_names();db.execute(f'UPDATE {t} SET {c[1]}=?,{c[2]}=?,{c[3]}=?,{c[4]}=?,{c[5]}=?,{c[6]}=? WHERE {c[0]}=?',(p['name'],p['category'],p['specs'],p['price'],p['stock'],p['image_url'],pid));flash('Изменения сохранены.','success');return redirect(url_for('index'))
 return render_template('edit_product.html',product=p)
@app.route('/delete/<int:pid>',methods=['POST'])
@admin_required
def delete_product(pid):
 t=db.table_name();c=db.column_names();db.execute(f'DELETE FROM {t} WHERE {c[0]}=?',(pid,));authdb.remove_product(pid);flash('Товар удалён.','success');return redirect(url_for('index'))
if __name__=='__main__':app.run(debug=True)
