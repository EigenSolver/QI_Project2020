import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import os
import plotly.graph_objects as go


# PLEASE INSTALL FOLLOWING PYTHON PACKAGES BEFORE FIRST RUNNING

cmd='''
conda install -c plotly plotly-orca
pip install psutil requests
'''
try:
    import psutil
except:
    print("PLEASE INSTALL FOLLOWING PYTHON PACKAGES BEFORE FIRST RUNNING")
    print(cmd)
    print("====================")
    

def data_plotter(file_path,plot_type="2D",fig_path="",fig_format=".svg",show_fig=False):
    
    
    file_name,file_extension=os.path.splitext(file_path)
    
    if plot_type is "":
        plot_type="2D"
    if fig_path is "":
        fig_path=file_name
    if fig_format is "":
        fig_format=".svg"

    # for excel and text format
    if file_extension==".xlsx":
        data_sheet=pd.read_excel(file_path)
        # Make data.
        theta=data_sheet["θ"]
        phi=data_sheet["ϕ"]
        try:
            p0=data_sheet.prob_0
        except:
            p0=data_sheet.prob_0_qubit_0
    
    elif file_extension==".txt":
        theta, phi, p0 = np.loadtxt(file_path,delimiter="\t",usecols=(0,1,2),unpack=True)

    else:
        raise TypeError("Unsupported file type.")

    x, y, z = np.cos(phi) * np.sin(theta), np.sin(phi) * np.sin(theta), np.cos(theta)
    # Plot the surface. F_measured/F_theory
    df = px.data.iris()


    if show_fig:
        fig.show()

    if plot_type =='3D':
        fig = px.scatter_3d(x, y, z, color=p0, template="plotly_white")
        plotly.offline.plot(fig, filename=fig_path)
    elif plot_type =='2D':
        fig = px.scatter_3d(x, y, z, color=p0, template="plotly_white")
        fig.write_image(fig_path+fig_format) 
    elif plot_type =='Proj':
        lat=np.pi/2-theta
        lon=phi-np.pi

        n_lat, n_lon = (30,10) 
        off_set=1e-3
        g_lat,g_lon = np.meshgrid(np.linspace(-np.pi/2+off_set,np.pi/2-off_set,n_lat), np.linspace(-np.pi+off_set,np.pi-off_set,n_lon))

        def hammar_map(lat,lon):
            kx=2*np.sqrt(2)*np.cos(lat)*np.sin(lon/2)/np.sqrt(1+np.cos(lon/2)*np.cos(lat))
            ky=np.sqrt(2)*np.sin(lat)/np.sqrt(1+np.cos(lon/2)*np.cos(lat))
            return mx,my
        
        def mollweide_map(lat,lon):
            A=lat
            for i in range(20):
                A=A-(2*A+np.sin(2*A)-np.pi*np.sin(lat))/(2+2*np.cos(2*A))

            kx=2*np.sqrt(2)*lon*np.cos(A)/np.pi
            ky=np.sqrt(2)*np.sin(A)
            return kx,ky 


        kx,ky=mollweide_map(lat,lon)
        gx,gy=mollweide_map(g_lat.flatten(),g_lon.flatten())
        
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=kx,y=ky,mode='markers',marker=dict(color=p0)))

        fig.add_trace(go.Scatter(x=gx,y=gy,mode='lines',line=dict(width=1)))

        # fig= px.scatter(x=kx,y=ky,color=p0)
        # fig.add_line(x=gx,y=gy)
        fig.update_yaxes(scaleanchor = "x", scaleratio = 1)
        fig.update_layout(coloraxis_colorbar=dict(title="Fidelity"),
            title="Bloch Sphere Projection",
            xaxis_title="x",
            yaxis_title="y",
            showlegend=False) 
        fig.write_image(fig_path+fig_format,scale=2) 
        

    else:
        raise ValueError("Unsupported Plot style")


    print("Number of points: ", len(x))
    print("Average fidelity: ", np.average(p0))
    print("Standard deviation: ", np.std(p0))
   
if __name__=='__main__':
#     file_path=input("Please input data file: \n")
#     plot_type=input("Please input data plot style (2D/3D, 2D by default):\n")
#     fig_path=input("Please input saved figure name (default to use same name):\n")
#     fig_format=input("Please input saved figure format (.jpg,.png,.svg, .svg by default):\n")
    
    file_path="Starmon5/data_sheet_starmon_Yuning.xlsx"
    plot_type="Proj"
    fig_path="./test"
    fig_format=".jpg"
    data_plotter(file_path,plot_type,fig_path,fig_format)
    
# you can use this as a module and wirte a script to batch your ploting task