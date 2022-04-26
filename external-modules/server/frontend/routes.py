"""
    Author Zotov Nikita
"""
from flask import render_template, request, flash, redirect

from modules.common.searcher import get_element_by_system_idtf
from modules.sentence_analysis_module.generator import set_system_idtf
from server.backend.nlp.flow import NLPService
from server.frontend.app import Application
from server.frontend.configurator import Configurator

configurator = Configurator()
app = Application(configurator)
service = NLPService()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/input', methods=('GET', 'POST'))
def input_text():
    if request.method == 'POST':
        article = request.form['title']
        text = request.form['content']

        if not article:
            flash('Text article is required!')
        elif service.get_text_by_article(article):
            flash('Text article is busy!')
        else:
            service.analyse_text_lexemes(text, article)
            return redirect(f'{configurator.get_server_url()}/{article}')

    return render_template('input.html')


@app.route('/<text_article>')
def show_text(text_article):
    text = service.get_text_by_article(text_article)

    return render_template(
        'show_text.html', text=text)


@app.route('/<text_article>/lexical_structure')
def show_text_lexical_structure(text_article):
    structure_idtf = str(text_article).replace(" ", "_") + "_lexical_structure"
    structure = get_element_by_system_idtf(structure_idtf)

    if not structure.is_valid():
        structure = service.get_text_lexical_structure(text_article)
        if structure.is_valid():
            set_system_idtf(structure, structure_idtf)

    return render_template(
        'show_text_lexical_structure.html',
        url=f"http://localhost:8000/?sys_id={structure_idtf}&scg_structure_view_only=true"
    )


@app.route('/<text_article>/lexemes_table')
def text_lexemes_table(text_article):
    lexemes = service.resolve_lexemes(text_article)

    return render_template('table.html', lexemes=lexemes, article=text_article)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html", error=error), 500

