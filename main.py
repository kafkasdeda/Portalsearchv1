import base64
from io import StringIO
import streamlit as st
from PIL import Image
import os
from streamlit_cropper import st_cropper
from google.protobuf.struct_pb2 import Struct

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_pb2, status_code_pb2

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.css-1q1n0ol.egzxvld0
{
   visibility: hidden; 
}
.viewerBadge_container__1QSob
{
   visibility: hidden; 
}

</style> """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


## Construct the communications channel and the object stub to call requests on.
# Note: You can also use a secure (encrypted) ClarifaiChannel.get_grpc_channel() however
# it is currently not possible to use it with the latest gRPC version
channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)
CONCEPT_ID = '1'
QUANT = '0'
metadata = (('authorization', 'Key 06656c88de5e44fda2499b99966ab482'),)


#userDataObject = resources_pb2.UserAppIDSet(user_id='mb14njwekdxv', app_id='DesignTypes')
userDataObject = resources_pb2.UserAppIDSet(user_id='mb14njwekdxv', app_id='DesignTypesV2')
@st.cache
def load_image(uimage):
    img=Image.open(uimage)
    return img


st.title("Please upload an image from left panel using \"Browse files\" button.")
uimage = st.sidebar.file_uploader("",type=["jpeg","jpg","png","webp"])  
#uimage = st.sidebar.camera_input("Take a picture")  


colsec = st.sidebar.radio(label="", options=["All", "Collection", "In Stock", "Know How"])





xs=st.sidebar.slider("Return top n images",min_value=10,max_value= 30,step=1,value=20)

realtime_update = st.sidebar.checkbox(label="Crop image in Real Time", value=True)
box_color = st.sidebar.color_picker(label="Box Color", value='#0000FF')

aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=["1:1", "16:9", "4:3", "2:3", "Free"])
scount = 1


aspect_dict = {
    "1:1": (1, 1),
    "16:9": (16, 9),
    "4:3": (4, 3),
    "2:3": (2, 3),
    "Free": None
}
aspect_ratio = aspect_dict[aspect_choice]

    


search_metadata = Struct()


if uimage is not  None:
    st.image(load_image(uimage),width=200)
    image64 = uimage.getvalue()

    
    if colsec == "In Stock":
        
        
        search_metadata.update({"Stok": "1"})


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
                        ],

 
                        filters=[
                            resources_pb2.Filter(
                                annotation=resources_pb2.Annotation(
                                    data=resources_pb2.Data(
                                        metadata=search_metadata
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
    elif colsec == "Know How" :
        search_metadata.update({"Stok": "0"})
        
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
                        ],
                    filters=[
                        resources_pb2.Filter(
                            annotation=resources_pb2.Annotation(
                                data=resources_pb2.Data(
                                    metadata=search_metadata
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
    else:
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


        #st.write("\tScore %.2f for annotation: %s off input: %s metadata ",  (hit.score, hit.annotation.id, hit.input.data.image.url))
        
        
        if 'Design' in hit.input.data.metadata:
            
            if 'Quantity'  in hit.input.data.metadata:
                
                Quantity = hit.input.data.metadata['Quantity']
                if Quantity == "0.00":
                    qstr =""
                else:
                    qstr =   Quantity + "mt. in stock."

                
                
                plink = hit.input.data.metadata['Design']
                st.header(plink)
                st.header(qstr)
                st.markdown( '<img src="' +  hit.input.data.image.url +'" width="700" />',unsafe_allow_html=True)
                st.markdown("""---""")
            else:
                plink = hit.input.data.metadata['Design'].replace(".jpg","")
                Quantity = '0'    
                plinkarr = plink.split("-",2)
                plink='https://portal.yunsa.com/product/' +plinkarr[0].replace(' ','-')+'-'+plinkarr[1]
                st.header("[" + plinkarr[0] + plinkarr[1] + '](' + plink + ')')
                st.markdown('<a href="' + plink + '">' + '<img src="' +  hit.input.data.image.url +'" width="700" /> </a>',unsafe_allow_html=True)
                st.markdown("""---""")


        
        if scount > xs:
            break
        scount +=1
