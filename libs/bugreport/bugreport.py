from ftplib import FTP_TLS as FTP
from StringIO import StringIO
import zipfile
import ssl

class BugReport(object):

    ftp_destination = "ftp.zerophone.org"

    def __init__(self, filename):
        self.zip_contents = StringIO()
        self.zip_contents.name = filename
        self.zip = zipfile.ZipFile(self.zip_contents, mode="w", compression=zipfile.ZIP_DEFLATED)

    def add_file(self, path):
        self.zip.write(path)

    def add_text(self, text, filename):
        self.zip.writestr(filename, text)

    def send(self):
        ftp = FTP(self.ftp_destination)
        ftp.set_debuglevel(2)
        ftp.ssl_version = ssl.PROTOCOL_TLSv1_2
        ftp.login()
        ftp.cwd("upload")
        ftp.prot_p()
        self.zip.close()
        self.zip_contents.seek(0)
        ftp.storbinary("STOR {}".format(self.zip_contents.name), self.zip_contents)


if __name__ == "__main__":
    filename = "zpui_bootlog_test.zip"
    report = BugReport(filename)
    report.add_file('config.json')
    report.add_text('"this is a description text"', 'description.json')
    report.send()
