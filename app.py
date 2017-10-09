from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.utils import secure_filename
from logging import Formatter, FileHandler
from time import strftime
import os, sys, csv

# create flask app
app = Flask(__name__)

# configurations
# app.config.from_object('config')
basedir = os.path.abspath(os.path.dirname(__file__))


# configure log handlers, log file: app.log
handler = FileHandler(os.path.join(basedir, './logs/app.log'), encoding='utf8')

handler.setFormatter(Formatter("[%(asctime)s] %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S"))
app.logger.addHandler(handler)

# path to upload folder
UPLOAD_FOLDER = os.path.join(basedir, './uploads')

# add file path to config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# create uploader folder if missing
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# allow csv files only
ALLOWED_EXTENSIONS = set(['csv'])

# app.secret_key = '999@#%!*SDNINiim'

# file extension checker
def allowed_file(file):
    """Does filename have the right extensions defined in ALLOWED_EXTENSIONS?"""
    return '.' in file and file.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# dictionary to store filenames for global use
dict_files = {}

# route: index/main
@app.route("/")
def main():
	return render_template('index.html')

# route: upload
@app.route("/upload", methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':

        # extract filenames in POST request
        file1 = request.files['file1']
        file2 = request.files['file2']

        # error message
        message = "Please select 2(csv) files!"

        # if none or only 1 file selected: prompt user, then exit
        if file1.filename == "" or file2.filename == "":
            app.logger.warning('None/only 1 selected file(s)! Exiting...')
            error_timestamp = strftime('[%Y-%b-%d %H:%M]')
            # app.logger.error(error_timestamp, 'None/only 1 selected file(s)! Exiting...')

            sys.exit()


        # -if 2 files received,
        # -check file extensions are valid using function: allowed_file.
        # -save file to upload folder

        try:
            if allowed_file(file1.filename) and allowed_file(file2.filename):
                filename1 = secure_filename(file1.filename)
                file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
                app.logger.info(file1.filename + ' is valid. File saved to /uploads.')

                app.logger.info(file1.filename + ' is valid. Uploading..')
                filename2 = secure_filename(file2.filename)
                file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
                app.logger.info(file2.filename + ' is valid. File saved to /uploads.')

                # store filename for global use
                dict_files['file1'] = filename1
                dict_files['file2'] = filename2

            else:
                message='Filetype for file not allowed. Exiting...'
                app.logger.error('Filetype for file not allowed. Exiting...')
                sys.exit()

        except KeyError or IndexError as error:
            app.logger.error('Filetype for file not allowed')

        return jsonify(message=message)
    return render_template('index.html')


# route: comparison results
@app.route("/showComparisonResults")
def showComparisonResults():


    file1_count=0
    file2_count=0


    # function remove_duplicate: check for duplicate records from file
    # write duplicates to tmp.csv file
    # rename from tmp.csv to original file name
    def remove_duplicate(*args):
        for file in args:
            with open(file, 'r') as file_reader, open('tmp.csv', 'w') as file_writer:
                reader = csv.reader(file_reader, delimiter=',')
                writer = csv.writer(file_writer, delimiter=',')

                entries = set()

                for row in reader:
                    key = (row[4], row[5])
                    if key not in entries:
                        writer.writerow(row)
                        entries.add(key)
                app.logger.info("Duplicate removed")
            os.rename('tmp.csv', file)

    # invoke remove_duplicate() on files
    remove_duplicate('uploads/' + dict_files['file1'], 'uploads/' + dict_files['file2'])

    # find count
    # open file1, file2
    try:
        with open('uploads/' + dict_files['file1']) as f1, open('uploads/' + dict_files['file2']) as f2:

            # first line is Header, ignore
            f1.readline()
            app.logger.info('Reading file: %s', dict_files['file1'])

            # get count
            for line in f1:
                file1_count+=1
            app.logger.info('Done reading file')

            # first line is Header, ignore
            f2.readline()
            app.logger.info('Reading file: %s', dict_files['file1'])

            # get count
            for line in f2:
                file2_count+=1
            app.logger.info('Done reading file')

    # handle ioError exception
    except IOError as error:
        app.logger.warning("Could not read files! .I/O error")

    # handle other exceptions such as attribute errors
    except:
        app.logger.info("Unexpected error")

    # find common records
    # open file1, file2, tmp
    with open('uploads/' + dict_files['file1'], 'r') as file1_reader, open('uploads/' + dict_files['file2'], 'r') as file2_reader, open('uploads/tmp.csv', 'w') as output:

        # initialize csv file reader/writer handlers
        csv1 = csv.reader(file1_reader)
        csv2 = csv.reader(file2_reader)
        tmp = csv.writer(output)

        # make file1 master file to compare file2 against
        master_list = list(csv1)

        # initialize match_count as -1 because of Header found in 0
        match_count = -1

        # loop through both csv file rows
        # files contain transactions, so i assume:
        # timestamp + amount + location + id + reference are vital and must be unique
        # row index slices from 1-8 gives columns after ProfileName column which is irrelevant
        # row[1] is Date
        # row[2] is Amount
        # row[3] is Narrative/Location
        # row[4] is Description
        # row[5] is Identifier/RRN
        # row[7] is Reference
        # if above columns+rows are same in both files:
        # write to tmp.csv file

        for file2_row in csv2:
            row = 1
            for master_row in master_list:

                results_matched = file2_row

                if (file2_row[1:8] == master_row[1:8]):
                    results_matched

                    match_count+=1

                    tmp.writerow(results_matched) # write matching records into tmp.csv
        app.logger.info("Matching records saved in uploads/tmp.csv")

    # find unmatched
    # open file1, file2, tmp
    with open('uploads/' + dict_files['file1']) as f1, open('uploads/' + dict_files['file2']) as f2, open('uploads/tmp.csv') as tmp:

        # read+split into rows
        a1 = f1.read().split('\n')
        a2 = f2.read().split('\n')
        tmp = tmp.read().split('\n')

        # convert to set data
        a1_set = set(a1)
        a2_set = set(a2)
        tmp_set = set(tmp)

        # find differences between file and tmp file
        # remember tmp contains common records between files

        # to find records in file1 but not in file2:
        # find records in file1 but not in tmp(common records between the two)
        diff1 = a1_set - tmp_set
        # find records in file2 but not in tmp(common records between the two)
        diff2 = a2_set - tmp_set

    # to get count of differences get len
    unmatched_count_file1 = len(diff1)
    unmatched_count_file2 = len(diff2)

    # inject variables into template for display
    return render_template('comparison_results.html',
                           dict_files=dict_files,
                           file1_count=file1_count,
                           file2_count=file2_count,
                           match_count=match_count,
                           unmatched_count_file1=unmatched_count_file1,
                           unmatched_count_file2=unmatched_count_file2,
                           )

@app.route("/showUnmatchedReports")
def showUnmatchedReports():

    # find unmatched
    with open('uploads/' + dict_files['file1']) as f1, open('uploads/' + dict_files['file2']) as f2, open('uploads/tmp.csv') as tmp:

        a1 = f1.read().split('\n')      # read and split lines to strings, file1
        a2 = f2.read().split('\n')      # read and split lines to strings, file2
        tmp = tmp.read().split('\n')    # read and split lines to strings, tmp.csv(common records between 2 files)

        # convert to set
        a1_set = set(a1)
        a2_set = set(a2)
        tmp_set = set(tmp)

        # get difference, between file1, file2 and tmp.csv
        diff1 = a1_set-tmp_set
        diff2 = a2_set-tmp_set

        # convert difference to comma delimited csv list
        reader1 = csv.reader(diff1)
        reader2 = csv.reader(diff2)

        # get row index representing columns, and form dictionary(headers are keys) using list comprehension
        # x[1]=Transaction Date
        # x[5]=Transaction ID
        # x[2]=Transaction amount

        reader1_dict = [{'TransactionDate': x[1], 'TransactionID': x[5], 'TransactionAmount': x[2]} for x in reader1]
        reader2_dict = [{'TransactionDate': x[1], 'TransactionID': x[5], 'TransactionAmount': x[2]} for x in reader2]

        # sort unmatched transactions by Transaction Date
        unmatched_file1_content = sorted(reader1_dict, key=lambda k: k['TransactionDate'])
        unmatched_file2_content = sorted(reader2_dict, key=lambda k: k['TransactionDate'])


        # log unmatched transactions
        app.logger.info("Unmatched transactions in " + dict_files['file1'])
        app.logger.info("-----------------------")
        app.logger.info(dict_files['file1'])
        app.logger.info(unmatched_file1_content)

        app.logger.info("Unmatched transactions in " + dict_files['file2'])
        app.logger.info("-----------------------")
        app.logger.info(dict_files['file2'])
        app.logger.info(unmatched_file2_content)


    # inject variables into template for display
    return render_template('unmatched_reports.html',
                           dict_files=dict_files,
                           unmatched_file1_content=unmatched_file1_content,
                           unmatched_file2_content=unmatched_file2_content
                           )



# run app in test server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
