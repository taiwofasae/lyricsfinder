# Lyrics finder

# deployment resources
- admin app
    - install packages and 'pip freeze > requirements.txt'
- mysql database
    - public access
    - create database name 'create database lyricsapp;'
    - migrate 'python manage.py migrate'
    - create superuser 'python migrate.py createsuperuser'
- s3 file system
    - block public access
- Q cluster (reddis queue/mongodb queue)
- settings and environment variables
- static file server
    - simple development server
    - S3 for static serving
    - cloudfront
- Embeddings
    - create embeddings table

# todo
- make endpoint for fetching lyrics data
- configure deployment settings
    - save/serve static files
- docker
- kubernetes
- abstract base class for file embeddings and s3 embeddings