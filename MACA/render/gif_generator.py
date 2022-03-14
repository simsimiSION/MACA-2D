
import imageio
import os


def gif_generate(save_path, duration=0.05):
    # get pics path
    current_path = os.path.split(os.path.realpath(__file__))[0] + '/tmp/'
    
    pic_names = os.listdir(current_path)
    if '.DS_Store' in pic_names:
        pic_names.remove('.DS_Store')
    if len(pic_names) == 0:
        return

    pic_names = sorted(pic_names, key=lambda x: int(x.split('.')[0]))
    pic_list = [current_path + '/' + pic_name for pic_name in pic_names]

    # save pics to gif
    frames = []
    for pic_dir in pic_list:
        frames.append(imageio.imread(pic_dir))

    imageio.mimsave(save_path, frames, 'GIF', duration=duration)
    
    # delete pics
    for pic_dir in pic_list:
        os.remove(pic_dir)

