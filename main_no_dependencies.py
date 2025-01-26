import os
from http.server import BaseHTTPRequestHandler, HTTPServer

VIDEO_PATH = "C:/Users/your-profile/Videos/video.mp4"

class VideoHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream-video':
            try:
                # Get the 'Range' header from the request
                range_header = self.headers.get('Range', None)

                # Get the size of the video file
                video_size = os.path.getsize(VIDEO_PATH)

                # If the Range header exists, handle partial content
                if range_header:
                    # Parse the range header (e.g., 'bytes=0-999999')
                    byte_range = range_header.strip().split('=')[1]
                    start_byte, end_byte = byte_range.split('-')
                    start_byte = int(start_byte)
                    end_byte = int(end_byte) if end_byte else video_size - 1

                    # Set the content length for the response
                    content_length = end_byte - start_byte + 1

                    # Open the video file in binary mode and send the range requested in chunks
                    with open(VIDEO_PATH, 'rb') as video_file:
                        video_file.seek(start_byte)

                        # Send HTTP 206 Partial Content response
                        self.send_response(206)
                        self.send_header('Content-Type', 'video/mp4')
                        self.send_header('Content-Range', f'bytes {start_byte}-{end_byte}/{video_size}')
                        self.send_header('Content-Length', str(content_length))
                        self.send_header('Accept-Ranges', 'bytes')
                        self.end_headers()

                        # Read and send the video in chunks (using default buffer size)
                        while chunk := video_file.read():
                            self.wfile.write(chunk)

                else:
                    # If no Range header is present, send the full video (HTTP 200 OK)
                    self.send_response(200)
                    self.send_header('Content-Type', 'video/mp4')
                    self.send_header('Content-Length', str(video_size))
                    self.end_headers()

                    # Send the entire video file in chunks
                    with open(VIDEO_PATH, 'rb') as video_file:
                        while chunk := video_file.read():
                            self.wfile.write(chunk)
            except BaseException as e:
                e=f"{type(e).__name__}: {str(e)}"
                self.send_response(500) # 500 Internal Server Error
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', str(len(e)))
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))

        else:
            # If the path is not '/', return a 404
            self.send_response(404)
            self.end_headers()

# Create and run the server
def run(server_class=HTTPServer, handler_class=VideoHTTPRequestHandler, port=8002):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()

