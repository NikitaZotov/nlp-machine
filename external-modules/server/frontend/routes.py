"""
    Author Zotov Nikita
"""
#from PyPDF2.pdf import PdfFileReader

from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

from modules.common.searcher import get_element_by_system_idtf
from modules.sentence_analysis_module.generator import set_system_idtf
from server.backend.nlp.flow import NLPService
from server.frontend.app import Application

app = Application()
service = NLPService()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/input', methods=('GET', 'POST'))
def input_text():
    if request.method == 'POST':
        if 'title' in request.form and 'content' in request.form:
            article = request.form['title']
            text = request.form['content']

            if not article:
                flash('Text article is required!')
            elif service.get_text_by_article(article):
                flash('Text article is busy!')
            elif text:
                service.add_text_instance(text, article)
                return redirect(f'{app.get_server_url()}/output/{article}')
        else:
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                article = filename.split(".")[0]

                if service.get_text_by_article(article):
                    flash('Text article is busy!')
                else:
                    text = read_pdf(file)
                    service.add_text_instance(text, article)

                    return redirect(f'{app.get_server_url()}/output/{article}')

    return render_template('input.html')


@app.route('/output/<text_article>')
def show_text(text_article):
    text = service.get_text_by_article(text_article)

    return render_template(
        'show_text.html', article=text_article, text=text)


@app.route('/output/<text_article>/lexical_structure')
def show_text_lexical_structure(text_article):
    structure_idtf = str(text_article).replace(" ", "_") + "_lexical_structure"
    structure = get_element_by_system_idtf(structure_idtf)

    if not structure.is_valid():
        structure = service.get_text_lexical_structure(text_article)
        if structure.is_valid():
            set_system_idtf(structure, structure_idtf)

    return render_template(
        'show_text_lexical_structure.html',
        article=text_article,
        scg_url=f"http://localhost:8000/?sys_id={structure_idtf}&scg_structure_view_only=true"
    )


@app.route('/output/<text_article>/syntactic_structure')
def show_text_syntactic_structure(text_article):
    structure_idtf = str(text_article).replace(" ", "_") + "_syntactic_structure"
    structure = get_element_by_system_idtf(structure_idtf)

    if not structure.is_valid():
        structure = service.get_text_syntactic_structure(text_article)
        if structure.is_valid():
            set_system_idtf(structure, structure_idtf)

    return render_template(
        'show_text_syntactic_structure.html',
        article=text_article,
        scg_url=f"http://localhost:8000/?sys_id={structure_idtf}&scg_structure_view_only=true"
    )


@app.route('/output/<text_article>/semantic_structure')
def show_text_semantic_structure(text_article):
    structure_idtf = str(text_article).replace(" ", "_") + "semantic_structure"
    structure = get_element_by_system_idtf(structure_idtf)

    if not structure.is_valid():
        structure = service.get_text_semantic_structure(text_article)
        if structure.is_valid():
            set_system_idtf(structure, structure_idtf)

    return render_template(
        'show_text_semantic_structure.html',
        article=text_article,
        scg_url=f"http://localhost:8000/?sys_id={structure_idtf}&scg_structure_view_only=true"
    )


@app.route('/output/<text_article>/lexemes_table')
def text_lexemes_table(text_article):
    lexemes = service.resolve_lexemes(text_article)

    return render_template('table.html', lexemes=lexemes, article=text_article)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':

        flash("Lexeme inserted successfully")

        return redirect(url_for('index'))


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':

        flash("Lexeme updated successfully")

        return redirect(url_for('index'))


@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    flash("Lexeme removed successfully")

    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html", error=error), 500


def read_pdf(file) -> str:
    # pdf = PdfFileReader(stream=file.stream)
    # first_page = pdf.getPage(0)
    # text = first_page.extractText()

    text = 'Ontology is the branch of philosophy that studies concepts such as existence, being, becoming, and reality.'

    return text
