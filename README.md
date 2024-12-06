#### 1. Data labeling via Electron(VPN이 되는 환경)

1-1) 라벨링 dcm 파일, single 프레임은 Sharpoint의 엑셀파일 참고 (eg. CoroCAT\LAO_file_paths.xlsx)

#### 2. labeling 좌표 추출

2-1) GPU 서버에서 mongo.py를 Local 컴퓨터로 옮긴다. VS code로 drag & drop 가능.

2-2) Local computer(VPN이 되는 환경)에서 mongo.py 실행, 

>> filename_prefix를 입력하시오: 병록번호/시행날짜/XA/0XX.dcm
>> 같은 디렉토리에 병록번호/시행날짜/XA\0XX.json 로 저장됨

#### 3. GPU 서버로 dcm, json 파일 전송

3-1) GPU 서버에서 send_dcm.py & send_json.py를 Local 컴퓨터로 옮긴다.

3-2) Local 컴퓨터에서 send_dcm.py & send_json.py 실행 

3-3) GUI로 send 할 폴더경로 설정

#### 4. GPU 서버에서 .dcm을 .mp4로, .json을 .pt(pytorch확장자)로 전환

4-1) GPU 서버에서 convert_dcm.py 실행

4-2) GPU 서버에서 tensor.py 실행
>> Enter the input JSON file path: 

#### 5. cotracker 가동

5-1) IDE로 start00.py 띄운다.

5-2) .mp4, .pt path 설정 및 backward tracking path, output_video_path 설정. 총 4군데를 바꿔줘야 한다.

(1) 
    # Read the video from the specified path
    #######path복붙

video = read_video_from_path('/home/user/DHKIM/CoroCAT/mp4/30004407/20200710/XA/007.mp4')

(2) 
    # Path to the .pt file containing queries
    #######path복붙

    file_path = '/home/user/DHKIM/CoroCAT/tensor/30004407/20200710/XA/007_frame_31.pt'

(3)
    # Backward tracking and visualization
    #######filename 수정

    try:
    pred_tracks, pred_visibility = model(video_tensor, queries=queries[None], backward_tracking=True)
    vis.visualize(
        video=video_tensor,
        tracks=pred_tracks,
        visibility=pred_visibility,
    >>>>>>>수정할 곳    filename='30004407_2020_0710_XA_007'
    )
    print("Visualization saved successfully.")
    except Exception as e:
    print(f"Error during visualization: {e}")

(4) 
    # Display the video
    #######filename 수정

    output_video_path = "./videos/30004407_2020_0710_XA_007.mp4"

5-3) start00.py 실행. output_video_path에 tracking된 video 인쇄되어 있음.
