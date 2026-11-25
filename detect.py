import warnings
warnings.filterwarnings('ignore')
from ultralytics import RTDETR



if __name__ == '__main__':
    model = RTDETR(r'')
    model.predict(source=r'',
    # model.predict(source=r'G:\RTDETR\RTDETR-20251008\RTDETR-main\compare_experiment\SSDD_compare',
                  conf=0.5,
                  project='runs/detect',
                  name='SSDD_detect',
                  save=True,
                #   visualize=True # visualize model features maps
                  line_width=1, # line width of the bounding boxes
                  show_conf=False, # do not show prediction confidence
                  show_labels=False, # do not show prediction labels
                  # save_txt=True, # save results as .txt file
                  # save_crop=True, # save cropped images with results
                  )