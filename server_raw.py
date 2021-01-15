from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from datetime import datetime
import zipfile
import shutil
from hurry.filesize import size, alternative
import threading

rec_path = "recordings/"

def get_contents(file):
    file = open('static/' + file, mode='r')
    content = file.read()
    file.close()
    return content

def get_sessions():
    # grab directories
    sessions = next(os.walk(rec_path))[1]

    # filter out hidden directories
    sessions = filter(lambda x: not x.startswith("."), sessions)

    # sort directories
    sessions = sorted(sessions)

    return sessions

def get_recordings(path):
    # grab files
    recordings = next(os.walk(path))[2]

    # filter out hidden files
    recordings = filter(lambda x: not x.startswith("."), recordings)

    # sort files
    recordings = sorted(recordings)

    return recordings

def get_session_size(path):
    nbytes = sum(d.stat().st_size for d in os.scandir(path) if d.is_file())
    return size(nbytes, system=alternative)

def get_session_date(path):
    return datetime.fromtimestamp(os.stat(path).st_mtime).strftime("%d. %b %Y")

def get_session_time(path):
    return datetime.fromtimestamp(os.stat(path).st_mtime).strftime("%H:%M")

def delete_path(path):
    path = path.strip("./")

    if not path.startswith(rec_path):
        return

    if not os.path.exists(path):
        return 

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        dirname = os.path.dirname(path)
        os.remove(path)

        # delete enclosing folder if empty
        if len(os.listdir(dirname)) == 0:
            shutil.rmtree(dirname)

def get_disk_usage():
    info = shutil.disk_usage(rec_path)
    myinfo = {
      "free": size(info.free, system=alternative),
      "used": size(info.total - info.free, system=alternative),
      "total": size(info.total, system=alternative),
      "percent_used": "{:.1f}".format((info.total - info.free) / info.total * 100) + "%",
      "percent_free": "{:.1f}".format(info.free / info.total * 100) + "%",
    }
    return myinfo

def zip_session(a, b, c, path):
    print("zipping...")
    print(a)
    print(b)
    print(c)
    print(path)
    return
    session_id = session_id.strip("./")
    session_id = int(session_id)
    session_id = f'{session_id:03}'
    shutil.make_archive("zips/session_"+str(session_id), 'zip', rec_path+str(session_id))
    print("done zipping")

def session_zip_exists(path):
    path = path.strip("/")
    return os.path.isfile("zips/session_" + path + ".zip")

class RecordingsServer(SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _html(self):

        index_html = get_contents('index.html')
        session_html = get_contents('session.html')
        recordings_html = get_contents('recording.html')

        all_sessions_html = ""
        sessions = get_sessions()
        for session_path in sessions:
            all_recordings_html = ""
            recordings = get_recordings(rec_path + session_path)
            size = get_session_size(rec_path+session_path)
            date = str(get_session_date(rec_path+session_path))
            time = str(get_session_time(rec_path+session_path))

            for filename in recordings:
                all_recordings_html += recordings_html \
                    .replace("{filename}", filename) \
                    .replace("{filepath}", rec_path + session_path + "/" + filename)

            all_sessions_html += session_html \
                .replace("{session_path}", session_path) \
                .replace("{zip_class}", "download" if session_zip_exists(session_path) else "zip") \
                .replace("{zip_path}", "zips/session_" + session_path + ".zip" if session_zip_exists(session_path) else "") \
                .replace("{recordings}", all_recordings_html) \
                .replace("{size}", size).replace("{date}", date) \
                .replace("{time}", time)

        disk_info = get_disk_usage()

        index_html = index_html \
            .replace("{sessions}", all_sessions_html) \
            .replace("{free}", disk_info['free']) \
            .replace("{used}", disk_info['used']) \
            .replace("{total}", disk_info['total']) \
            .replace("{percent_used}", disk_info['percent_used']) \
            .replace("{percent_free}", disk_info['percent_free'])

        return index_html.encode("utf8")

    def do_GET(self):
        if (self.path == "/"):
            self._set_headers()
            self.wfile.write(self._html())
            return

        if (self.path == "favico.ico"):
            self._set_headers()
            self.wfile.write(b"")
            return

        if (self.path.startswith("/delete/")):
            self._set_headers()
            delete_path(self.path[8:]);
            return

        if (self.path.startswith("/zip/")):
            x = threading.Thread(target=zip_session, args=("1234"))
            x.start()
            x.join()
            #zip_session(self.path[5:])
            self._set_headers()
            return

        super().do_GET()


def run(server_class=HTTPServer, handler_class=RecordingsServer, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(    'Starting httpd...')
    httpd.serve_forever()

get_disk_usage()
run()