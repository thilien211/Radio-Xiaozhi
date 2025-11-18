"""
Xiaozhi Adapter - VOV RADIO STREAM VERSION
Chuyển đổi từ AAC++ sang MP3 stream realtime với tìm kiếm thông minh
"""

from flask import Flask, request, jsonify, Response
import requests
import subprocess
import os
import re
from difflib import SequenceMatcher

app = Flask(__name__)

PORT = int(os.environ.get('PORT', 5005))

# DANH SÁCH CÁC KÊNH VOV RADIO
RADIO_STATIONS = {
    'vov1': {
        'name': 'VOV 1 - Kênh Thời Sự',
        'url': 'https://stream.vovmedia.vn/vov-1',
        'artist': 'VOV 1',
        'keywords': ['vov 1', 'vov1', 'thời sự', 'tin tức']
    },
    'vov2': {
        'name': 'VOV 2 - Kênh Thông Tin',
        'url': 'https://stream.vovmedia.vn/vov-2',
        'artist': 'VOV 2',
        'keywords': ['vov 2', 'vov2', 'thông tin']
    },
    'vov3': {
        'name': 'VOV 3 - Kênh Âm Nhạc',
        'url': 'https://stream.vovmedia.vn/vov-3',
        'artist': 'VOV 3',
        'keywords': ['vov 3', 'vov3', 'âm nhạc', 'nhạc']
    },
    'vov5': {
        'name': 'VOV 5 - Kênh Đối Ngoại',
        'url': 'https://stream.vovmedia.vn/vov5',
        'artist': 'VOV 5',
        'keywords': ['vov 5', 'vov5', 'đối ngoại']
    },
    'vovgt-hn': {
        'name': 'VOV Giao Thông Hà Nội',
        'url': 'https://stream.vovmedia.vn/vovgt-hn',
        'artist': 'VOV Giao Thông HN',
        'keywords': ['giao thông hà nội', 'giao thông hanoi', 'gt hà nội', 'gt hn', 'vovgt hn']
    },
    'vovgt-hcm': {
        'name': 'VOV Giao Thông TP.HCM',
        'url': 'https://stream.vovmedia.vn/vovgt-hcm',
        'artist': 'VOV Giao Thông HCM',
        'keywords': ['giao thông hồ chí minh', 'giao thông hcm', 'giao thông sài gòn', 'gt hcm', 'vovgt hcm']
    },
    'vov247': {
        'name': 'VOV Tiếng Anh',
        'url': 'https://stream.vovmedia.vn/vov247',
        'artist': 'VOV English',
        'keywords': ['vov 247', 'vov247', 'tiếng anh', 'english', 'vov tieng anh']
    },
    'vovmekong': {
        'name': 'VOV Mê Kông',
        'url': 'https://stream.vovmedia.vn/vovmekong',
        'artist': 'VOV Mê Kông',
        'keywords': ['mê kông', 'mekong', 'vov mekong', 'vov me kong']
    },
    'vov4mt': {
        'name': 'VOV Miền Trung',
        'url': 'https://stream.vovmedia.vn/vov4mt',
        'artist': 'VOV Miền Trung',
        'keywords': ['miền trung', 'mien trung', 'vov 4 miền trung', 'vov4 mt']
    },
    'vov4tb': {
        'name': 'VOV Tây Bắc',
        'url': 'https://stream.vovmedia.vn/vov4tb',
        'artist': 'VOV Tây Bắc',
        'keywords': ['tây bắc', 'tay bac', 'vov 4 tây bắc', 'vov4 tb']
    },
    'vov4db': {
        'name': 'VOV Đông Bắc',
        'url': 'https://stream.vovmedia.vn/vov4db',
        'artist': 'VOV Đông Bắc',
        'keywords': ['đông bắc', 'dong bac', 'vov 4 đông bắc', 'vov4 db']
    },
    'vov4tn': {
        'name': 'VOV Tây Nguyên',
        'url': 'https://stream.vovmedia.vn/vov4tn',
        'artist': 'VOV Tây Nguyên',
        'keywords': ['tây nguyên', 'tay nguyen', 'vov 4 tây nguyên', 'vov4 tn']
    },
    'vov4dbscl': {
        'name': 'VOV Đồng Bằng Sông Cửu Long',
        'url': 'https://stream.vovmedia.vn/vov4dbscl',
        'artist': 'VOV ĐBSCL',
        'keywords': ['đồng bằng sông cửu long', 'dong bang song cuu long', 'đbscl', 'dbscl', 'vov 4 dbscl']
    },
    'gtduyenhai': {
        'name': 'VOV Duyên Hải',
        'url': 'https://stream.vovmedia.vn/gtduyenhai',
        'artist': 'VOV Duyên Hải',
        'keywords': ['duyên hải', 'duyen hai', 'gt duyên hải', 'vov duyen hai']
    },
    'fm89': {
        'name': 'VOV FM89 - Âm Nhạc Trẻ',
        'url': 'https://stream.vovmedia.vn/fm89',
        'artist': 'VOV FM89',
        'keywords': ['fm 89', 'fm89', 'vov fm89', 'âm nhạc trẻ']
    }
}

# Lưu station đang phát
current_station = {'id': 'vov3', 'info': RADIO_STATIONS['vov3']}


def normalize_text(text):
    """Chuẩn hóa text để tìm kiếm"""
    if not text:
        return ""
    # Loại bỏ dấu tiếng Việt
    text = text.lower()
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    text = re.sub(r'[đ]', 'd', text)
    # Loại bỏ ký tự đặc biệt, giữ space
    text = re.sub(r'[^\w\s]', ' ', text)
    # Loại bỏ space thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def similarity_score(str1, str2):
    """Tính độ tương đồng giữa 2 chuỗi"""
    return SequenceMatcher(None, str1, str2).ratio()


def find_best_station(query):
    """Tìm station phù hợp nhất với query"""
    if not query:
        return current_station['id'], current_station['info']
    
    normalized_query = normalize_text(query)
    print(f"🔍 Normalized query: '{normalized_query}'")
    
    best_match = None
    best_score = 0
    
    for station_id, station_info in RADIO_STATIONS.items():
        # Tìm trong name
        normalized_name = normalize_text(station_info['name'])
        score_name = similarity_score(normalized_query, normalized_name)
        
        # Tìm trong keywords
        max_keyword_score = 0
        for keyword in station_info['keywords']:
            normalized_keyword = normalize_text(keyword)
            keyword_score = similarity_score(normalized_query, normalized_keyword)
            
            # Kiểm tra substring match (điểm cao hơn)
            if normalized_query in normalized_keyword or normalized_keyword in normalized_query:
                keyword_score = max(keyword_score, 0.8)
            
            max_keyword_score = max(max_keyword_score, keyword_score)
        
        # Tổng điểm (ưu tiên keyword)
        total_score = max(score_name, max_keyword_score)
        
        print(f"  - {station_id}: {total_score:.2f} (name: {score_name:.2f}, keyword: {max_keyword_score:.2f})")
        
        if total_score > best_score:
            best_score = total_score
            best_match = (station_id, station_info)
    
    # Nếu không tìm thấy gì phù hợp (< 0.4), giữ station hiện tại
    if best_score < 0.4:
        print(f"⚠️ No good match (score: {best_score:.2f}), using current station: {current_station['id']}")
        return current_station['id'], current_station['info']
    
    print(f"✅ Best match: {best_match[0]} (score: {best_score:.2f})")
    return best_match


@app.route('/stream_pcm', methods=['GET'])
def stream_pcm():
    """
    Endpoint tương thích với Xiaozhi với tìm kiếm thông minh
    """
    global current_station
    
    try:
        query = request.args.get('song', '')
        
        print(f"\n{'='*60}")
        print(f"📻 Request: '{query}'")
        
        # Tìm station phù hợp nhất
        station_id, station = find_best_station(query)
        
        # Cập nhật current station
        current_station = {'id': station_id, 'info': station}
        
        print(f"🎵 Selected: {station['name']} (ID: {station_id})")
        
        # Chuẩn bị response
        result = {
            'artist': station['artist'],
            'audio_url': f"/proxy_audio?id={station_id}",
            'cover_url': '',
            'duration': 0,  # Radio là vô hạn
            'from_cache': False,
            'lyric_url': '',  # Radio không có lyric
            'title': station['name']
        }
        
        print(f"✅ Response: {result}")
        print(f"{'='*60}\n")
        return jsonify(result)
        
    except Exception as error:
        print(f"❌ Error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/proxy_audio', methods=['GET'])
def proxy_audio():
    """
    Stream audio từ radio station với chuyển đổi AAC++ -> MP3
    """
    try:
        station_id = request.args.get('id')
        
        # Nếu không có ID, dùng current station
        if not station_id:
            station_id = current_station['id']
            
        if station_id not in RADIO_STATIONS:
            station_id = current_station['id']
        
        station = RADIO_STATIONS[station_id]
        radio_url = station['url']
        
        print(f"🎵 Streaming: {station['name']}")
        print(f"🔗 URL: {radio_url}")
        
        def generate():
            """Generator function để stream MP3 data"""
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', radio_url,
                '-vn',  # Không video
                '-acodec', 'libmp3lame',  # Chuyển sang MP3
                '-ab', '128k',  # Bitrate 128kbps
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Stereo
                '-f', 'mp3',  # Format MP3
                '-',  # Output to stdout
                '-loglevel', 'error',  # Chỉ hiện lỗi
                '-reconnect', '1',  # Tự động reconnect
                '-reconnect_streamed', '1',
                '-reconnect_delay_max', '5'
            ]
            
            try:
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=10**5  # Buffer 100KB
                )
                
                print(f"✅ FFmpeg started for {station_id}")
                
                # Stream data chunks
                while True:
                    chunk = process.stdout.read(4096)  # 4KB chunks
                    if not chunk:
                        break
                    yield chunk
                
                process.wait()
                print(f"⏹️ Stream ended for {station_id}")
                
            except Exception as e:
                print(f"❌ FFmpeg error: {str(e)}")
                if 'process' in locals():
                    process.kill()
        
        return Response(
            generate(),
            mimetype='audio/mpeg',
            headers={
                'Cache-Control': 'no-cache',
                'X-Content-Type-Options': 'nosniff',
                'Transfer-Encoding': 'chunked'
            }
        )
        
    except Exception as error:
        print(f"❌ Proxy audio error: {str(error)}")
        return 'Failed to stream audio', 500


@app.route('/proxy_lyric', methods=['GET'])
def proxy_lyric():
    """Radio không có lyric"""
    return 'Radio streams do not have lyrics', 404


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'stations': len(RADIO_STATIONS),
        'current_station': {
            'id': current_station['id'],
            'name': current_station['info']['name']
        },
        'available_stations': list(RADIO_STATIONS.keys())
    })


@app.route('/stations', methods=['GET'])
def list_stations():
    """Liệt kê tất cả các kênh radio"""
    stations_list = []
    for station_id, station_info in RADIO_STATIONS.items():
        stations_list.append({
            'id': station_id,
            'name': station_info['name'],
            'artist': station_info['artist'],
            'keywords': station_info['keywords']
        })
    
    return jsonify({
        'total': len(stations_list),
        'current': current_station['id'],
        'stations': stations_list
    })


if __name__ == '__main__':
    print('=' * 60)
    print(f"📻 Xiaozhi Radio Adapter (VOV Stations)")
    print(f"🎵 Port: {PORT}")
    print(f"📡 Total stations: {len(RADIO_STATIONS)}")
    print(f"🔧 FFmpeg required for AAC++ to MP3 conversion")
    print(f"🧠 Smart search enabled with fuzzy matching")
    print('=' * 60)
    print("\n📻 Available stations:")
    for station_id, info in RADIO_STATIONS.items():
        print(f"  - {info['name']}")
        print(f"    Keywords: {', '.join(info['keywords'][:3])}")
    print('=' * 60)
    
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
