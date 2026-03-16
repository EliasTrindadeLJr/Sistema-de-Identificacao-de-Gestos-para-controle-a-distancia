from pygrabber.dshow_graph import FilterGraph

def camera_extract():
    graph = FilterGraph()
    available_cameras = graph.get_input_devices()
    return available_cameras

available_camera = camera_extract()