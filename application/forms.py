from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Email, Regexp
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from application.models import User


class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")


class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField("Sign In")

class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = CKEditorField('Content', validators=[DataRequired()])
	type_choices = [('Travel','Travel'),('Food','Food'),('Health & Fitness','Health & Fitness'),('Lifestyle','Lifestyle'),
						('Fashion & Beauty','Fashion & Beauty'),('Photography','Photography'),('Personal','Personal'),('Movies','Movies'),('Sports','Sports')]
	category = SelectField(label='Category', choices=type_choices , validators=[DataRequired()])
	image = FileField("Add Image/Media", validators=[FileRequired(), FileAllowed(["jpg", "png","jpeg","gif","mp4","mpeg2","avi"],message="Wrong Image Format")])
	submit = SubmitField("Submit")

class EditPostForm(FlaskForm):
	title = StringField("Title", validators=[Optional()])
	content = CKEditorField('Content', validators=[Optional()])
	type_choices = [('Travel','Travel'),('Food','Food'),('Health & Fitness','Health & Fitness'),('Lifestyle','Lifestyle'),
						('Fashion & Beauty','Fashion & Beauty'),('Photography','Photography'),('Personal','Personal'),('Movies','Movies'),('Sports','Sports')]
	category = SelectField(label='Category', choices=type_choices , validators=[Optional()])
	image = FileField("Add Image/Media", validators=[Optional(), FileAllowed(["jpg", "png","jpeg","gif","mp4","mpeg2","avi"],message="Wrong Image Format")])
	submit = SubmitField("Submit")	

class RegistrationForm(FlaskForm):
	fname = StringField("First Name", validators=[DataRequired()])
	lname = StringField("Last Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20,message='Minimum lenght of username should be 4 characters long')])
	email = StringField("Email", validators=[DataRequired(),Email()])
	dob = StringField("Birthday",validators=[DataRequired()])
	profession = StringField(label='Profession',validators=[DataRequired()])
	location = StringField("Location")
	password_hash = PasswordField('Password', validators=[DataRequired()])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password_hash', message='Passwords Must Match!')])
	profile_pic = FileField("Add Profile Picture", validators=[FileAllowed(["jpg", "png","jpeg","gif"],message="Wrong Image Format")])
	submit = SubmitField("Register")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username already in use.','warning')

		excluded_chars = " *?!'^+%&/()=}][{$#@"
		for char in username.data:
			if char in excluded_chars:
				raise ValidationError(
                    f"Character {char} is not allowed in username.",'warning')	

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email already registered.')

class ChangePasswordForm(FlaskForm):
	current_password = PasswordField("Current Password", validators=[DataRequired()])
	new_password = PasswordField("New Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
	submit = SubmitField("Submit")


class ChangePicForm(FlaskForm):
	profile_pic = FileField("Add Profile Picture", validators=[FileAllowed(["jpg", "png","jpeg","gif"],message="Wrong Image Format")])
	submit = SubmitField("Submit")

class EditProfileForm(FlaskForm):
	fname = StringField("First Name")
	lname = StringField("Last Name")
	username = StringField("Username")
	email = StringField("Email",validators=[Optional(), Email()])
	profession = StringField("Profession")
	location = StringField("Location")
	mobile = StringField('Contact',validators=[Optional(), Length(min=10, max=10,message='Mobile number should be 10 characters long'),Regexp(regex='^[7-9][0-9]{9}$',message='Invalid Phone Number!')])
	dob = StringField("Birthday")	
	submit = SubmitField("Save Changes")

	def validate_username(self, username):
		excluded_chars = " *?!'^+%&/()=}][{$#"
		for char in username.data:
			if char in excluded_chars:
				raise ValidationError(
                    f"Character {char} is not allowed in username.")


class CommentForm(FlaskForm):
	comment = StringField("Comment", validators=[DataRequired()], widget=TextArea())
	submit = SubmitField("Post Comment")

class ForgotForm(FlaskForm):
	email = StringField("Email",validators=[DataRequired(), Email()]) 
	dob = StringField("Birthday",validators=[DataRequired()])
	submit = SubmitField("Submit")
