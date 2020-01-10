from trectools.misc import remove_punctuation
from lxml import etree
import codecs
from bs4 import BeautifulSoup
import os
import re


class TrecTopics:

    def __init__(self, topics={}):
        self.topics = topics

    def read_topics_from_file(self, filename, topic_tag="topic", numberid_tag="number", number_attr=True,
                              querytext_tag="query", title_regex=None, debug=False, number_regex=None):
        """
            Reads a xml file into a TrecTopics object. Example:
            <topics>
            <topic number="201" type="single">
                <query>amazon raspberry pi</query>
                <description> You have heard quite a lot about cheap computing as being the way of the future,
                including one recent model called a Raspberry Pi. You start thinking about buying one, and wonder how much they cost.
                </description>
            </topic>
            </topics>

            If your query number is a tag <number> 201 </number>, set number_attr = False.

        """
        # TODO: throw an exception for errors when reading the topics.
        soup = BeautifulSoup(codecs.open(filename, "r"), "lxml")

        for topic in soup.findAll(topic_tag):
            if number_attr:
                topic_id = topic.get(numberid_tag)
            else:
                topic_id = topic.findNext(numberid_tag).findAll(text=True, recursive=False)[0].strip()
            if number_regex:
                m = re.match(number_regex, topic_id)
                topic_id = int(m.group(1))

            query = topic.findNext(querytext_tag).findAll(text=True, recursive=False)[0].strip()
            if title_regex:
                m = re.match(title_regex, query)
                query = m.group(1)
            if debug:
                print("Number: %s Query: %s" % (topic_id, query))
            self.topics[topic_id] = query

    def set_topics(self, topics):
        self.topics = topics

    def set_topic(self, topic_id, topic_text):
        self.topics[topic_id] = topic_text

    def clean_topics(self):
        result = {}
        for topid, text in self.topics.items():
            cleaned_text = remove_punctuation(text)
            result[topid] = cleaned_text
        self.topics = result

    def printfile(self, filename="output.xml", fileformat="terrier", outputdir=None, debug=True):
        """
            Writes out the topics to a file.
            After one runs this method, TrecTopics.outputfile is available with the
            filepath to the created file.
            fileformat: terrier, indri, indribaseline or anserini
        """
        if outputdir is None:
            outputdir = os.getcwd()

        self.outputfile = os.path.join(outputdir, filename)
        if debug:
            print("Writing topics to %s" % self.outputfile)
        xml_str_list = []

        if fileformat == "terrier":
            # Creates file object
            root = etree.Element('topics')
            for qid, text in sorted(self.topics.items(), key=lambda x: x[0]):
                topic = etree.SubElement(root, 'top')
                tid = etree.SubElement(topic, 'num')
                tid.text = str(qid)
                ttext = etree.SubElement(topic, 'title')
                ttext.text = text
        elif fileformat == "indri" or fileformat == "indribaseline":
            root = etree.Element('parameters')
            trecformat = etree.SubElement(root, 'trecFormat')
            trecformat.text = "true"
            for qid, text in sorted(self.topics.items(), key=lambda x: x[0]):
                topic = etree.SubElement(root, 'query')
                tid = etree.SubElement(topic, 'id')
                tid.text = str(qid)
                ttext = etree.SubElement(topic, 'text')
                cleaned_text = remove_punctuation(text)
                if fileformat == "indri":
                    ttext.text = "#combine( " + cleaned_text + " )"
                elif fileformat == "indribaseline":
                    ttext.text = cleaned_text
        elif fileformat == "anserini":
            for qid, text in sorted(self.topics.items(), key=lambda x: x[0]):
                topic = etree.Element('top')
                tid = etree.SubElement(topic, 'num')
                tid.text = f' Number:  {qid}'
                ttext = etree.SubElement(topic, 'title')
                ttext.text = f' Topic:  {text}'
                etree.SubElement(topic, 'desc').text = ''  # text='' to create an empty tag: <desc></desc>
                etree.SubElement(topic, 'narr').text = ''
                xml_str = str(etree.tostring(topic, pretty_print=True, encoding='unicode'))
                xml_str = re.sub(r'\n\s+', '\n', xml_str)  # remove identation
                xml_str_list.append(xml_str)

        xml_str = '\n'.join(xml_str_list) if xml_str_list else str(
            etree.tostring(root, pretty_print=True, encoding='unicode'))
        with open(self.outputfile, "w") as f:
            f.writelines(xml_str)
