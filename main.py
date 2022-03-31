import base64

from io import StringIO
from quopri import encodestring
import streamlit as st
from PIL import Image
import os
from streamlit_cropper import st_cropper
from google.protobuf.struct_pb2 import Struct

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_pb2, status_code_pb2
import mysql.connector
from mysql.connector import Error



## Construct the communications channel and the object stub to call requests on.
# Note: You can also use a secure (encrypted) ClarifaiChannel.get_grpc_channel() however
# it is currently not possible to use it with the latest gRPC version
channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key bfec9a0decfd41eba484fb2b042937b6'),)


userDataObject = resources_pb2.UserAppIDSet(user_id='mb14njwekdxv', app_id='DesignTypes')

@st.cache
def load_image(uimage):
    img=Image.open(uimage)
    return img


st.title("Please upload an image.")
uimage = st.sidebar.file_uploader("",type=["jpeg","jpg","png","webp"])  
#uimage = st.sidebar.camera_input("Take a picture")  
realtime_update = st.sidebar.checkbox(label="Crop image in Real Time", value=True)
box_color = st.sidebar.color_picker(label="Box Color", value='#0000FF')
aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=["1:1", "16:9", "4:3", "2:3", "Free"])
xs=st.sidebar.slider("Return top n images",min_value=10,max_value= 30,step=1,value=20)

scount = 1


aspect_dict = {
    "1:1": (1, 1),
    "16:9": (16, 9),
    "4:3": (4, 3),
    "2:3": (2, 3),
    "Free": None
}
aspect_ratio = aspect_dict[aspect_choice]

    





if uimage is not  None:
    st.image(load_image(uimage),width=200)
    image64 = uimage.getvalue()

    
   
    post_annotations_searches_response = stub.PostAnnotationsSearches(
    service_pb2.PostAnnotationsSearchesRequest(
        searches = [
            resources_pb2.Search(
                query=resources_pb2.Query(
                    ranks=[
                        resources_pb2.Rank(
                            annotation=resources_pb2.Annotation(
                                data=resources_pb2.Data(
                                    image=resources_pb2.Image(
                                        base64=image64
                                    )
                                )
                            )
                        )
                    ]
                )
            )
        ]
    ),
    metadata=metadata
    )
    #st.write(post_annotations_searches_response)

    if post_annotations_searches_response.status.code != status_code_pb2.SUCCESS:
        print("There was an error with your request!")
        print("\tCode: {}".format(post_annotations_searches_response.status.code))
        print("\tDescription: {}".format(post_annotations_searches_response.status.description))
        print("\tDetails: {}".format(post_annotations_searches_response.status.details))
        raise Exception("Post searches failed, status: " + post_annotations_searches_response.status.description)

    print("Search result:")
    for hit in post_annotations_searches_response.hits:


        print("\tScore %.2f for annotation: %s off input: %s metadata ",  (hit.score, hit.annotation.id, hit.input.data.image.url))
        
        
        if 'Design' in hit.input.data.metadata:
            plink = hit.input.data.metadata['Design'].replace(".jpg","")
            plinkarr = plink.split("-",2)
            plink='https://portal.yunsa.com/product/' +plinkarr[0].replace(' ','-')+'-'+plinkarr[1]
            st.write("[" + plinkarr[0] + plinkarr[1] + '](' + plink + ')')
            st.markdown('<a href="' + plink + '">' + '<img src="' +  hit.input.data.image.url +'" width="700" /> </a>',unsafe_allow_html=True)
            


        
        if scount > xs:
            break
        scount +=1
