from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from datetime import datetime
import zipfile
import shutil
import zipstream
import web
from web.httpserver import StaticMiddleware
import bitmath


rec_path = "recordings/"

def get_contents(file):
    file = open('static/' + file, mode='r')
    content = file.read()
    file.close()
    return content

def get_size(bytes, precision):
    return str(bitmath.Byte(bytes).best_prefix(system=bitmath.SI).format("{value:." + str(precision) + "f} {unit}"))

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
    return get_size(nbytes, 1)

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
      "free": get_size(info.free, 0),
      "used": get_size(info.total - info.free, 0),
      "total": get_size(info.total, 1),
      "percent_used": "{:.1f}".format((info.total - info.free) / info.total * 100) + "%",
      "percent_free": "{:.1f}".format(info.free / info.total * 100) + "%",
    }
    return myinfo

def create_and_stream_zip(session_path):

    # nested generator function to stream chunks of zip
    def generator(zip_folder_name):

        # create zip stream
        zf = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

        # add empty session folder to zip
        zf.write(rec_path + session_path + "/", arcname=zip_folder_name + "/")

        # iterate recording files in session
        for recording in get_recordings(rec_path + session_path):
            # write bytes to stream
            zf.write(rec_path + session_path + "/" + recording, arcname=zip_folder_name + "/" + recording)

        # iterate all bytes of all files and yield back
        for chunk in zf:
            yield chunk


    zip_name = "wavedeck-session-" + session_path

    # set headers
    web.header('Content-type' , 'application/zip')
    web.header('Content-Disposition', 'attachment; filename="%s"' % (zip_name + ".zip",))

    return generator(zip_name)

def html():

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
            .replace("{zip_path}", "zip/" + session_path) \
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


urls = (
  "/", "index",
  "/delete/(.*)", "delete",
  "/zip/(.*)", "zip"
)

class index:
    def GET(self):
        return html()

class delete:
    def GET(self, session_path):
        delete_path(session_path)
        return "ok"

class zip:
    def GET(self, session_path):
        return create_and_stream_zip(session_path)

class AddStaticMiddlewareRecordings(StaticMiddleware):
    def __init__(self, app, prefix="/" + rec_path):
        StaticMiddleware.__init__(self, app, prefix)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run(AddStaticMiddlewareRecordings)