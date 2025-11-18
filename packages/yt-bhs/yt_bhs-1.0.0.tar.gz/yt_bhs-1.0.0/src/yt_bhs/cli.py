
# Program to download Youtube songs with proper metadata and cover art.

import json, shutil

from PIL import Image
from pathlib import Path
from hashlib import sha1

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename, DownloadError
from argparse import ArgumentParser

from colorama import init as color_init
from colorama import Fore, Style
color_init()


def red(text):
	return Fore.LIGHTRED_EX + str(text) + Style.RESET_ALL
def cyan(text):
	return Fore.LIGHTCYAN_EX + str(text) + Style.RESET_ALL
def yellow(text):
	return Fore.LIGHTYELLOW_EX + str(text) + Style.RESET_ALL


def log(msg, VERBOSE):
	if VERBOSE:
		print(msg)


# For generating unique album titles
def simple_hash(hash_input, label):
	# Only first 3 characters of hash code used
	code = sha1(hash_input.encode()).hexdigest()[:3]
	return label + ' · ' + code


# To make text compatible with the file system
def sanitize(text):
	if '.' in text[-1]:
		text = text.replace('.', '·')
	text = sanitize_filename(text)
	return text


def file_exists(filepath, verbose):
	if not filepath.is_file():
		log(f'There is no file at "{filepath}"', verbose)
		return 0
	
	file_size = filepath.stat().st_size
	if file_size == 0:
		log(f'The file "{filepath}" is empty.', verbose)
		return 0
	
	return 1


def check_song(directory, title, args):
	output_dir = args.output / directory
	print('Checking local storage for', title)
	if not output_dir.is_dir():
		log(f'Output directory does not exist at "{output_dir}". Creating one.', args.verbose)
		# parents - if true, creates parent dirs if not exists
		# exist_ok - if true, doesn't throw error if path exists
		output_dir.mkdir(parents=True, exist_ok=True)
		return 0
	
	final_song = output_dir / (title + '.mp3')
	if not file_exists(final_song, args.verbose):
		return 0

	print(yellow('Already exists, moving on...\n'))
	return 1


def check_cache(directory, title, args):
	playlist_dir = args.cache_dir / directory
	song_dir = playlist_dir / title 
	temp_song = song_dir / 'backup.mp3'
	cropped_img = song_dir / 'crop.png'
	final_song = song_dir / (title + '.mp3')
	
	if not playlist_dir.is_dir():
		log(f'Playlist directory does not exist at "{playlist_dir}". Creating one.', args.verbose)
		playlist_dir.mkdir(parents=True, exist_ok=True)
		
	if not song_dir.is_dir():
		log(f'Song directory does not exist at "{song_dir}". Creating one.', args.verbose)
		song_dir.mkdir()

	cache = {
		'got_song': file_exists(temp_song, args.verbose),
		'has_cropped': file_exists(cropped_img, args.verbose),
		'finalized': file_exists(final_song, args.verbose),
	}
	
	if cache['got_song']:
		log(yellow(f'Temporary song "{temp_song}" already downloaded.'), args.verbose)
	
	# Accounting for variations of thumbnail formats
	file_lst = list(song_dir.glob('**/*'))
	for file in file_lst:
		if file.stem == 'thumb':
			cache['got_thumb'] = 1
			log(yellow(f'Temporary thumbnail "{file}" already downloaded.'), args.verbose)
			break
	else:
		cache['got_thumb'] = 0
	
	if cache['has_cropped']:
		log(yellow(f'Thumbnail already cropped at "{cropped_img}".'), args.verbose)
	
	if cache['finalized']:
		log(yellow(f'Ready to copy song already available at "{final_song}".'), args.verbose)
	
	return cache


def download_song(url, directory, title, args):
	song_dir = args.cache_dir / directory / title
	
	print('Starting download...')
	ydl_opts = {
		'format': 'bestaudio',
		'outtmpl': str(song_dir / 'backup.%(ext)s'),
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '96',
		}],
	}
	
	if not args.verbose:
		ydl_opts['quiet'] = True
		ydl_opts['no_warnings'] = True
	
	with YoutubeDL(ydl_opts) as ydl:
		try:
			ydl.download([url])
		except DownloadError:
			print(red('ERROR:'), 'Unable to download audio track.')
			return 0
			
	print(cyan('Song downloaded.'))
	return 1


def download_thumb(url, directory, title, args):
	song_dir = args.cache_dir / directory / title
	
	print('Downloading thumbnail...')
	ydl_opts = {
		'outtmpl': str(song_dir / 'thumb.%(ext)s'),
		'writethumbnail': True,
		'skip_download': True,
	}
	
	if not args.verbose:
		ydl_opts['quiet'] = True
		ydl_opts['no_warnings'] = True
		
	with YoutubeDL(ydl_opts) as ydl:
		try:
			ydl.download([url])
		except DownloadError:
			print(red('ERROR:'), 'Unable to download video thumbnail.')
			return 0
	
	print(cyan('Thumbnail downloaded.'))
	return 1


# For thumbnails that aren't in PNG format
def convert_thumb(directory, title, args):
	song_dir = args.cache_dir / directory / title
	file_lst = list(song_dir.glob('**/*'))
	for file in file_lst:
		if file.stem != 'thumb':
			continue
		
		if file.suffix == '.png':
			print('Conversion not required, thumbnail already in PNG format.')
			return

		log(f'Thumbnail found with format: "{file}"', args.verbose)
		with Image.open(file) as img:
			log('Converting thumbnail to PNG format.', args.verbose)
			img.save(song_dir / 'thumb.png')
				
		log(f'Successfully converted thumbnail, saved at "{file}".', args.verbose)


# For getting square thumbnails
def crop_thumb(directory, title, args):
	song_dir = args.cache_dir / directory / title
	temp_thumb = song_dir / 'thumb.png'
	cropped_img = song_dir / 'crop.png'
	
	with Image.open(temp_thumb) as img_file:
		width, height = img_file.size
		log(f"Original thumbnail's resolution: {width} x {height}", args.verbose)

		# Only crop to square if not already
		if width != height:
			h_offset = 0
			new_height = height
			ratio = width / height
			log(f"Original thumbnail's aspect ratio: {ratio}", args.verbose)

			# Checking for height offset (for 4:3 ratio thumbnails)
			# yt-dlp thumbnail fallback edgecase
			if ratio != (16/9):
				new_height = height / (4/3)
				h_offset = (height - new_height) // 2
				log(f'Height cropped to {new_height} with offset {h_offset}', args.verbose)
				
			# Setting width offset
			w_offset = (width - new_height) // 2
			log(f'Width cropped to {new_height} with offset {w_offset}', args.verbose)
			
			left = w_offset
			top = h_offset
			right = width - w_offset
			bottom = height - h_offset
			log(f'Crop parameters: LEFT-{left} TOP-{top} RIGHT-{right} BOTTOM-{bottom}', args.verbose)

			area = (left, top, right, bottom)
			img_file = img_file.crop(area)
			
		img_file.save(cropped_img)
		log(f'Thumbnail cropped successfully and saved at "{cropped_img}".', args.verbose)


def add_meta(data, song, directory, title, args):
	song_dir = args.cache_dir / directory / title
	temp_song = song_dir / 'backup.mp3'
	meta_song = song_dir / 'song.mp3'
	shutil.copy2(temp_song, meta_song)
	
	artist = data[song]['artist']
	date = data[song]['dateAdded']

	# Adding metadata
	log('Embedding textual metadata in the song.', args.verbose)
	tags = EasyID3(meta_song)
	tags['title'] = title
	tags['artist'] = artist
	tags['album'] = simple_hash(title, artist)
	tags['albumartist'] = artist
	tags['genre'] = 'Youtube'
	tags['tracknumber'] = '1'
	tags['date'] = date
	tags.pprint()
	tags.save()
	
	print(cyan('Metadata added.'))
	

def add_cover(directory, title, args):
	song_dir = args.cache_dir / directory / title
	meta_song = song_dir / 'song.mp3'
	final_song = song_dir / (title + '.mp3')
	img_path = song_dir / 'crop.png'
	
	with open(img_path, 'rb') as img_file:
		log('Retrieving binary data of cropped thumbnail.', args.verbose)
		img_data = img_file.read()		# Binary data for APIC
	
	# Adding cover art
	audio = MP3(meta_song, ID3=ID3)
	log('Embedding cover art.', args.verbose)
	audio.tags.add(APIC(mime='image/png', type=3, data=img_data))
	audio.save()
	print(cyan('Thumbnail embedded.'))
	
	# Renaming temp file with song title
	meta_song.rename(final_song)
	log(f'Final song generated at "{final_song}"', args.verbose)


def copy_song(directory, title, args):
	source = args.cache_dir / directory / title / (title + '.mp3')
	output_dir = args.output / directory
	shutil.copy2(source, output_dir)
	log(f'Song successfully saved at "{output_dir}".', args.verbose)
	print(cyan('Finalized'), title, '\n')


def clean_cache(directory, args, title=None, ):
	playlist_dir = args.cache_dir / directory
	if title is not None:
		song_dir = playlist_dir / title
		if song_dir.is_dir():
			log(f'Removing song cache stored at "{song_dir}".', args.verbose)
			shutil.rmtree(song_dir)
	else:
		if playlist_dir.is_dir():
			log(f'Removing playlist directory located at "{playlist_dir}".', args.verbose)
			shutil.rmtree(playlist_dir)

  
def main():
	parser = ArgumentParser(prog='yt-bhs', description='Download Youtube Songs with Metadata')
	parser.add_argument('--test-run', dest='to_test', action='store_true')
	parser.add_argument('--keep-cache', dest='to_cache', action='store_true')
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('--cache-dir',
						type=Path,
						default=Path('cache'))
	parser.add_argument('-o', '--output',
						type=Path,
						default=Path('export'))
	parser.add_argument('playlist')
	
	args = parser.parse_args()
	
	playlist = args.playlist
	directory = playlist.split('.')[0]
	
	with open(playlist, 'r', encoding='utf-8') as json_file:
		data = json.load(json_file)

	if args.to_test:
		print(cyan('\nTest run selected. Only the first song will be downloaded.\n'))

	for song in data:
		title = sanitize(data[song]['title'])
		url = data[song]['perma_url']
		
		# Check if song is already downloaded
		found = check_song(directory, title, args)
		if found:
			continue
		
		# Check if any suitable cache already exists
		cache = check_cache(directory, title, args)
		
		# Downloading the song if available
		if not cache['got_song']:
			song_done = download_song(url, directory, title, args)
			if not song_done:
				break

		# Downloading the thumbnail 
		if not cache['got_thumb']:
			thumb_done = download_thumb(url, directory, title, args)
			if not thumb_done:
				break
			
		# Convert the thumbnail if not PNG
		convert_thumb(directory, title, args)

		# Crop the cover art if needed
		if not cache['has_cropped']:
			crop_thumb(directory, title, args)

		if not cache['finalized']:
			# Adding the metadata manually
			add_meta(data, song, directory, title, args)
		
			# Embedding the thumbnail as cover art
			add_cover(directory, title, args)
		
		# Copy the song to music folder
		copy_song(directory, title, args)
		
		if not args.to_cache:
			clean_cache(directory, args, title)
		
		if args.to_test:
			if not args.to_cache:
				clean_cache(directory, args)
			break
		
	else:
		if not args.to_cache:
			clean_cache(directory, args)
		print(cyan('Finished all downloads.'), 'Closing...')


if __name__ == "__main__":
	main()