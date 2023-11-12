from decouple import config
from flask import Flask, render_template, redirect, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

from workflow_delegate import delegate_workflow

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def hello_world():
    return redirect('/search', code=302)


@app.route('/search')
def display_search():
    return render_template('search.html')


@app.route('/view-results')
def display_view_results():
    client = MongoClient(config('MONGO_URL'))
    db = client['contactsdb']
    collection = db['contacts']
    data = list(collection.find())
    client.close()
    return render_template('view_results.html', data=data)


@app.route('/search-results')
def search_results():
    keyword = request.args.get('query')
    try:
        results = delegate_workflow(keyword)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print('Server running on http://localhost:8888')
    app.run(host='0.0.0.0', port=8888, debug=True)

