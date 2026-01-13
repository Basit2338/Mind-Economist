import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Post, Subscriber, Comment, SiteSettings, Submission, Category, ServiceOrder, Attachment
from app import db

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'exe', 'msi', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import re
def slugify(s):
    s = str(s).lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

@main.route('/')
def index():
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    if category:
        query = Post.query.filter_by(category=category).order_by(Post.created_at.desc())
        featured_posts = []
    else:
        query = Post.query.order_by(Post.created_at.desc())
        featured_posts = Post.query.filter_by(featured=True).order_by(Post.created_at.desc()).limit(5).all()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items

    if request.args.get('load_more'):
        return render_template('partials/post_grid_items.html', posts=posts)

    return render_template('index.html', posts=posts, featured_posts=featured_posts, current_category=category, pagination=pagination)

@main.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).order_by(Comment.created_at.desc()).all()
    return render_template('post.html', post=post, comments=comments)

@main.route('/about')
def about_us():
    return render_template('about_us.html')

@main.route('/services')
def services():
    return render_template('services.html')

@main.route('/service-order', methods=['POST'])
def submit_service_order():
    try:
        order = ServiceOrder(
            service_name=request.form.get('service_name'),
            customer_name=request.form.get('customer_name'),
            contact_number=request.form.get('contact_number'),
            age=int(request.form.get('age')) if request.form.get('age') else None,
            sex=request.form.get('sex'),
            location=request.form.get('location'),
            message=request.form.get('message')
        )
        db.session.add(order)
        db.session.commit()
        flash('Thank you! We will contact you shortly.')
        return redirect(url_for('main.services'))
    except Exception as e:
        flash('Something went wrong. Please try again.')
        return redirect(url_for('main.services'))

@main.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        posts = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) | 
            (Post.content.ilike(f'%{query}%'))
        ).order_by(Post.created_at.desc()).all()
    else:
        posts = []
    return render_template('search.html', posts=posts, query=query)
import random

@main.route('/submit', methods=['GET', 'POST'])
def submit_article():
    # Generate captcha for GET requests
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    
    if request.method == 'POST':
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', 'World')
        
        # Captcha validation
        captcha_answer = request.form.get('captcha_answer')
        expected_answer = request.form.get('captcha_expected')
        
        if not captcha_answer or captcha_answer != expected_answer:
            flash('Please solve the math puzzle correctly.')
            return render_template('submit.html', num1=num1, num2=num2, form_data=request.form)
        
        # Image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                import time
                filename = f"{int(time.time())}_{filename}"
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                image_url = f"uploads/{filename}"
        
        if author_name and author_email and title and content:
            submission = Submission(
                author_name=author_name,
                author_email=author_email,
                title=title,
                content=content,
                category=category,
                image_url=image_url
            )
            db.session.add(submission)
            db.session.commit()
            flash('Thank you! Your article has been submitted for review.')
            return redirect(url_for('main.submit_article'))
    
    return render_template('submit.html', num1=num1, num2=num2)

@main.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    name = request.form.get('name')
    email = request.form.get('email')
    content = request.form.get('content')
    
    if name and email and content:
        comment = Comment(name=name, email=email, content=content, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!')
    return redirect(url_for('main.post_detail', slug=post.slug) + '#comments')

@main.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def admin_reply(comment_id):
    parent_comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')
    
    if content:
        reply = Comment(
            name='Mind Economists',
            email='admin@economist.com',
            content=content,
            post_id=parent_comment.post_id,
            parent_id=comment_id,
            is_admin_reply=True
        )
        db.session.add(reply)
        db.session.commit()
        flash('Reply posted!')
    return redirect(url_for('main.post_detail', slug=parent_comment.post.slug) + '#comment-' + str(comment_id))

@main.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        existing = Subscriber.query.filter_by(email=email).first()
        if existing:
            flash('You are already subscribed!')
        else:
            new_subscriber = Subscriber(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash('Thank you for subscribing!')
    return redirect(request.referrer or url_for('main.index'))

# Admin Routes

@main.route('/dashboard')
@login_required
def dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    subscribers = Subscriber.query.order_by(Subscriber.subscribed_at.desc()).all()
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    service_orders = ServiceOrder.query.order_by(ServiceOrder.created_at.desc()).all()
    return render_template('dashboard.html', posts=posts, subscribers=subscribers, submissions=submissions, categories=categories, settings=settings, service_orders=service_orders)

@main.route('/submission/<int:submission_id>/approve', methods=['POST'])
@login_required
def approve_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    
    # Create a new post from the submission
    # Generate slug for new post
    base_slug = slugify(submission.title)
    slug = base_slug
    counter = 1
    while Post.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    post = Post(
        title=submission.title,
        content=submission.content,
        category=submission.category,
        author_id=current_user.id,
        contributor_name=submission.author_name,
        image_url=submission.image_url,
        slug=slug
    )
    db.session.add(post)
    
    # Mark submission as approved
    submission.status = 'approved'
    db.session.commit()
    
    flash(f'Article "{submission.title}" by {submission.author_name} has been published!')
    return redirect(url_for('main.dashboard') + '#submissions')

@main.route('/submission/<int:submission_id>/reject', methods=['POST'])
@login_required
def reject_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    submission.status = 'rejected'
    db.session.commit()
    flash(f'Submission "{submission.title}" has been rejected.')
    return redirect(url_for('main.dashboard') + '#submissions')

@main.route('/submission/<int:submission_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if request.method == 'POST':
        submission.title = request.form.get('title')
        submission.content = request.form.get('content')
        submission.category = request.form.get('category')
        db.session.commit()
        flash('Submission updated!')
        return redirect(url_for('main.dashboard') + '#submissions')
    return render_template('edit_submission.html', submission=submission)

@main.route('/settings', methods=['POST'])
@login_required
def save_settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
    
    settings.facebook_url = request.form.get('facebook_url', '')
    settings.instagram_url = request.form.get('instagram_url', '')
    settings.twitter_url = request.form.get('twitter_url', '')
    settings.whatsapp_url = request.form.get('whatsapp_url', '')
    settings.youtube_url = request.form.get('youtube_url', '')
    
    db.session.commit()
    flash('Social links saved successfully!')
    return redirect(url_for('main.dashboard') + '#settings')

@main.route('/category/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name', '').strip()
    if name:
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash(f'Category "{name}" already exists.')
        else:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{name}" added successfully!')
    return redirect(url_for('main.dashboard') + '#categories')

@main.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{name}" deleted.')
    return redirect(url_for('main.dashboard') + '#categories')

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        image_url = None
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                import time
                filename = f"{int(time.time())}_{filename}"
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                image_url = f"uploads/{filename}"
        
        if not title or not content:
            flash('Title and Content are required!')
        else:
            featured = request.form.get('featured') == 'on'
            
            # Generate slug
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Post.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            new_post = Post(title=title, content=content, category=category, image_url=image_url, featured=featured, author=current_user, slug=slug)
            db.session.add(new_post)
            db.session.commit() # Commit to get ID
            
            # Handle attachments
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        import time
                        filename = f"{int(time.time())}_{filename}"
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
                        os.makedirs(upload_folder, exist_ok=True)
                        file.save(os.path.join(upload_folder, filename))
                        attachment = Attachment(filename=file.filename, file_path=f"uploads/attachments/{filename}", post_id=new_post.id)
                        db.session.add(attachment)
                db.session.commit()

            return redirect(url_for('main.dashboard'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('create_post.html', categories=categories)

@main.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.category = request.form.get('category')

        # Update slug if title changed (optional, but good practice). 
        # For now, let's update it to ensure it matches title.
        base_slug = slugify(post.title)
        slug = base_slug
        counter = 1
        # Check uniqueness, excluding current post
        while Post.query.filter(Post.slug==slug, Post.id!=post.id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        post.slug = slug
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                post.image_url = f"uploads/{filename}"
        post.featured = request.form.get('featured') == 'on'
        
        # Handle attachments
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    filename = f"{int(time.time())}_{filename}"
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, filename))
                    attachment = Attachment(filename=file.filename, file_path=f"uploads/attachments/{filename}", post_id=post.id)
                    db.session.add(attachment)

        db.session.commit()
        return redirect(url_for('main.dashboard'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('create_post.html', post=post, categories=categories)

@main.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('main.dashboard'))
