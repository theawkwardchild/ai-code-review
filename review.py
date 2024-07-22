# windows:
# python -m venv openai-env
# openai-env\Scripts\activate
# pip install --upgrade openai

# linux:
# sudo apt install python3.10-venv # may or maynot be necessary for you
# python3 -m venv env 
# source env/bin/activate
# pip install openai


import argparse
from openai import OpenAI
import json
from os.path import exists # could also be useful when checking if context files exist to provide to chatGPT
import datetime
# import bleach # used to sanitize code you want to show in an HTML file
import html

def main():
    parser = argparse.ArgumentParser(description="A CLI tool that takes a URL as an argument.")
    parser.add_argument('-f', '--file', type=str, required=True, help='The file to process')
    
    args = parser.parse_args()
    openai_key = open("openai_key", "r").read()
    client = OpenAI(api_key=openai_key)
    if not exists(args.file):
        print("The provided file does not exist")
        exit()
    # read file provided as argument
    code_file = open(args.file, 'r')
    code = code_file.read()
    clean_code = html.escape(code)
    file_name = ""

    # when writing a file, it cannot contain a slash
    if args.file.find("/") != -1:
        file_name = (args.file[args.file.rfind("/") + 1:])
    else:
        file_name = (args.file[args.file.rfind("\\") + 1:])

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a security expert who gives advice on writing secure code and\
          provies easy to understand examples of correct code. Review my code and report and security issues.\
          If you require any additional files for context, list them. After I submit my code file I would like\
          a response in the format of a JSON object with the following keys: {'highlighted_code': ['code block 1',\
          'code block 2', 'code block 3'], 'security_issue': ['issue 1', 'issue 2', 'issue 3'], 'required_context_files'\:\
          ['../file1.config', './index.php', '../../scrips/main.js']}. Do not respond with any further explanations\
          or comments beyond the JSON object. Do not feel the need to find any security issues that do not exist.\
          Reassess any findings you first discover to ensure acuracy. Ensure each highlighted code block matches teh security issue."},
        {"role": "user", "content": args.file + "\n\n" + code}
    ]
    )
    clean_response = completion.choices[0].message.content
    clean_response = clean_response[clean_response.find("{"):clean_response.rfind("}") + 1]
    code_review = json.loads(clean_response)
            
    # We might want to add a check to ensure ChatGPT returned a JSON object in the format we expect
    # {"highlighted_code": [], "security_issue": [], "required_context_files": []}

    if(len(code_review['highlighted_code']) != len(code_review['security_issue'])):
        print("Oops! Our ChatGPT response contained an error. highlighted_code.length != security_issue.length. Our output may be incorrect.")
        # TODO: something could be added here to try to fix the response


    # TODO: do something about providing any context files required for the code review and rerunning the assessment

    for index, highlighted_code in enumerate(code_review['highlighted_code']):
        highlighted_code = html.escape(highlighted_code)
        clean_code = clean_code.replace(highlighted_code, '<span style="background-color: rgba(255, 0, 0, 0.15); border: 2px dotted  rgb(89, 35, 35);" onclick="togglePopup(this)" class="popup">' + highlighted_code + '<span class="popuptext" >' + code_review['security_issue'][index] + '</span></span>')

    # create an HTML file with the highlighted code and the security issues
    # filename(without any "/" or "\") - review - date.html
    # sanitize the code returned from openAI
    # match the highlighted_code to the code in our file. Surround the highlighted portion with some HTML to display the issues and mark the code in red


    output_file_name = file_name + " - review - " + str(datetime.datetime.now()).replace(":", "-") + ".html"
    output_header = "Code Review of " + file_name
    if(len(code_review['highlighted_code']) != len(code_review['security_issue'])):
        output_header += " <span style='color: red;'>[WARNING CHATGPT RETURNED IMPORPER RESPONSE]</span>"
    with open((output_file_name), 'w') as html_file:
        html_file.write('''
    <html>
        <head>
            <title>Code Review</title>
            <style>
            /* Popup container - can be anything you want */
            .popup {
                position: relative;
                display: inline-block;
                cursor: pointer;
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
            }
            /* The actual popup */
            .popup .popuptext {
                visibility: hidden;
                background-color: #555;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 8px 0;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -80px;
            }
            /* Popup arrow */
            .popup .popuptext::after {
                content: "";
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #555 transparent transparent transparent;
            }
            /* Toggle this class - hide and show the popup */
            .popup .show {
                visibility: visible;
                -webkit-animation: fadeIn 1s;
                animation: fadeIn 1s;
            }                        
            pre {
                font-size: 1.3em;
                padding: 15px;
            }                        
            /* Add animation (fade in the popup) */
            @-webkit-keyframes fadeIn {
                from {opacity: 0;} 
                to {opacity: 1;}
            }
            @keyframes fadeIn {
                from {opacity: 0;}
                to {opacity:1 ;}
            }
            </style>
            <script>
                function togglePopup(e) {
                    e.children[0].classList.toggle('show');
                }
            </script>
        </head>
        <body>
            <h1>''' + output_header + '''</h1>
            <pre><code>''' + clean_code + '''</code></pre>
        </body>
    </html>'''
    )

if __name__ == "__main__":
    main()