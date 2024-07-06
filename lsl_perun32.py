from pylsl import StreamInlet, resolve_stream

def start_stream(stream_name):
    '''
    Rozpoczęcie streamu z Peruna 32.
    :param save_path: Ścieżka zapisu danych
    :param stream_name: Nazwa streamu, taka sama jaką użyto w svarog_streamer
    :return:
    '''
    # znajdujemy streamy
    print("Looking for Perun32 streams...")
    streams = resolve_stream('type', 'EEG')

    selected_stream = None
    for stream in streams:
        if stream.name() in stream_name:
            selected_stream = stream
            print("Stream has been found")
    if selected_stream is None:
        print("Nie znalesiono streamu", stream_name, "w liście", [i.name() for i in streams])
        exit()

    inlet = StreamInlet(selected_stream)

    return inlet