"""
    Author Zotov Nikita
"""
from flask import render_template, request, flash, redirect, url_for


from server.backend.nlp.flow import AgentsService
from server.frontend.app import Application
from server.frontend.configurator import Configurator

configurator = Configurator()
app = Application(configurator)
service = AgentsService()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/input', methods=('GET', 'POST'))
def input_text():
    if request.method == 'POST':
        article = request.form['title']
        text = request.form['content']

        if not article:
            flash('Article is required!')
        else:
            service.analyse_text_lexemes(text, article)
            return redirect(url_for('index'))

    return render_template('input.html', mimetype="text/event-stream")


@app.route('/<text_article>')
def show_text(text_article):
    text = service.get_text_by_article(text_article)

    return render_template('show.html', text=text)


@app.route('/<text_article>/lexemes_table')
def text_lexemes_table(text_article):
    lexemes = service.resolve_lexemes(text_article)
    print(lexemes)

    return render_template('table.html', lexemes=lexemes, article=text_article)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html", error=error), 500

