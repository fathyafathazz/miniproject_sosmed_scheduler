from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

# Fungsi untuk membaca data dari file JSON
def load_data():
    if not os.path.exists('data.json'):
        return []
    with open('data.json', 'r') as f:
        return json.load(f)

# Fungsi untuk menyimpan data ke file JSON
def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Fungsi untuk mendapatkan id baru
def get_new_id(posts):
    if not posts:
        return 1
    else:
        return max(post['id'] for post in posts) + 1

# Data dummy untuk postingan
posts = load_data()

# Fungsi untuk mengurutkan postingan berdasarkan planned_publish_date dan urgency
def schedule_posts(posts):
    def sort_key(post):
        # Urutkan berdasarkan planned_publish_date (format %Y-%m-%d)
        date = datetime.strptime(post['planned_publish_date'], '%Y-%m-%d')
        urgency_order = {
            'CRITICAL': 1,
            'HIGH': 2,
            'MEDIUM': 3,
            'LOW': 4
        }.get(post['urgency'], 5)  # Default 5 for unknown urgencies
        return date, urgency_order

    sorted_posts = sorted(posts, key=sort_key)
    return sorted_posts

# Endpoint untuk mendapatkan semua postingan yang sudah diurutkan berdasarkan planned_publish_date dan urgency
@app.route('/posts', methods=['GET'])
def get_posts():
    sorted_posts = schedule_posts(posts)
    formatted_posts = [
        {
            "id": post["id"],
            "caption": post["caption"],
            "planned_publish_date": post["planned_publish_date"],
            "platform": post["platform"],
            "status": post["status"],
            "title": post["title"],
            "urgency": post["urgency"]
        }
        for post in sorted_posts
    ]
    return jsonify(formatted_posts)

# Endpoint untuk menambahkan postingan baru
@app.route('/posts', methods=['POST'])
def add_post():
    new_post = request.get_json()
    new_post['id'] = get_new_id(posts)
    posts.append(new_post)
    save_data(posts)
    return jsonify({'message': 'Post added successfully'}), 201

# Endpoint untuk memperbarui postingan berdasarkan id
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    updated_post = request.get_json()
    for post in posts:
        if post['id'] == post_id:
            post.update(updated_post)
            save_data(posts)
            return jsonify({'message': 'Post updated successfully'}), 200
    return jsonify({'message': 'Post not found'}), 404

# Endpoint untuk menghapus postingan berdasarkan id
@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global posts
    initial_length = len(posts)
    posts = [post for post in posts if post['id'] != post_id]
    if len(posts) < initial_length:
        save_data(posts)
        return jsonify({'message': 'Post deleted successfully'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)