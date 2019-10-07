#coding:utf-8
from flask import Flask,render_template,flash,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired


app=Flask(__name__)

class config(object):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI="mysql://root:@127.0.0.1:3306/author_book"
    SQLALCHEMY_TRACK_MODFICATIONS=True
    SECRET_KEY="SSKLDJFOIEJSF"


app.config.from_object(config)

db=SQLAlchemy(app)

class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    books = db.relationship("Book",backref="author")

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    author_id = db.Column(db.Integer,db.ForeignKey(Author.id))

class AuthorForm(FlaskForm):
    author = StringField('作者',validators=[DataRequired()])
    book = StringField('书籍',validators=[DataRequired()])
    submit = SubmitField('提交')


@app.route('/',methods=['GET','POST'])
def index():
    author_form = AuthorForm()
    if author_form.validate_on_submit():
        author_name = author_form.author.data
        book_name = author_form.book.data

        author = Author.query.filter_by(name=author_name).first()
        if author:
            book = Book.query.filter_by(name=book_name).first()
            if book:
                flash('已存在相同书籍')
            else:
                try:
                    new_book = Book(name=book_name,author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()
        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name,author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('添加作者和书籍失败')
                db.session.rollback()
    else:
        if request.method == "POST":
            flash('参数错误')
    authors = Author.query.all()
    return render_template('books.html',authors=authors,form=author_form)


@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author:
        try:
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者失败')
            db.session.rollback()
    else:
        flash('找不到作者')

    return redirect(url_for('index'))

@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍失败')
            db.session.rollback()
    else:
        flash('找不到书籍')

    return redirect(url_for('index'))


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    au1 = Author(name="wang")
    db.session.add_all(au1)
    db.session.commit()
    bk1 = Book(name="ww")
    db.session.add_all(bk1)
    db.session.commit()
    app.run()

