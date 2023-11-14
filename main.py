from flask import Flask, render_template, redirect, request
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
client = OpenAI()
#OPENAI_API_KEY='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'
app = Flask(__name__)



def extract_text_from_webpage(url):
    try:
        # Set a custom User-Agent header to mimic a web browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # Send an HTTP GET request to the URL with custom headers
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the webpage
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all the text elements on the webpage
            text_elements = soup.find_all(text=True)

            # Join the text elements into a single string
            page_text = ' '.join(text_elements)

            return page_text
        else:
            return f"Failed: Status Code {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def sourceDatatoText(source):
    refrence = source['Author'] +'. ('+ source['Year'] +'). ' + source["Title"] +'. [online] '+ source['Publisher']+'. Available at: ' + source['URL']
    return (refrence)

mysources = []
mysource = {'Author': 'John Smith', 'Year': '2019', 'Month': '05', 'Day': '17', 'Title': 'History of Blah blah blah', "Publisher": "ArticleSpot", "URL": "www.articlespot.com/12345678"}
mysources.append(mysource)
print (sourceDatatoText(mysource))
@app.route('/')
def load_main():
    global mysources
    myRefs = []
    for i in mysources:
        myRefs.append(sourceDatatoText(i))
    return render_template('main.html', sources = myRefs)

@app.route('/newsource', methods = ['GET','POST'])
def newsource():
    global defaults
    return render_template('addsource.html', author = defaults['Author'],
                           title = defaults["Title"], year = defaults["Year"], month = defaults["Month"],
                           publisher = defaults["Publisher"], day = defaults['Day'] ,url = defaults["URL"])


@app.route('/submitsource', methods = ['GET','POST'])
def submitsource():
    global mysources
    mysource = {'Author': request.form.get('author'),
                'Year': request.form.get('year'),
                'Month': request.form.get('month'),
                'Day': request.form.get('day'),
                'Title': request.form.get('title'),
                "Publisher": request.form.get('publisher'),
                "URL": request.form.get('url')}
    mysources.append(mysource)
    return redirect('/')

@app.route('/gptsource', methods = ['GET','POST'])
def gptsource():
    global defaults
    text = extract_text_from_webpage(request.form.get('url'))
    print (text)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system",
             "content": r"From the text that will follow this introductory section, determine the author, publisher, publication year, month, day and title. Output the info in this format and in this order. author: john smith > title: article about something > year: 1992 > month: 06 > day: 15 > publisher: example journal, If there is info that cannot be found, just put NONE for that peice of info. Use any reasonable date found on the page as the date if no clear date can be found. Year can include or omit the first two digits, 23 is okay, 2023 is also okay. OUTPUT ONLY TEXT IN THIS FORMAT. SAY NOTHING ELSE. This is the text: "+text}
        ]
    )
    gptOut = str(completion.choices[0].message.content)
    print (gptOut)
    gptOut = gptOut.split('>')
    print (gptOut)
    outlist = []
    for i in gptOut:
        outlist.append(i.split(':')[1])
    print (outlist)
    defaults = {
        'Author': outlist[0],
        'Title': outlist[1],
        'Year': outlist[2],
        'Month': outlist[3],
        'Day': outlist[4],
        'Publisher': outlist[5],
        'URL':  request.form.get('url')
    }
    print (defaults)

    return redirect('/newsource')




if __name__ == '__main__':
    app.run(debug=True)
