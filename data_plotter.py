import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import os


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
        p0=data_sheet.prob_0
    
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
        fig = px.scatter_3d(df, x, y, z, color=p0/(5/6), template="plotly_white")
        plotly.offline.plot(fig, filename=fig_path)
    elif plot_type =='2D':
        fig = px.scatter_3d(df, x, y, z, color=p0/(5/6), template="plotly_white")
        fig.write_image(fig_path+fig_format) 
    elif plot_type =='Proj':
        mx=x[z<0]/(1-z[z<0])
        my=y[z<0]/(1-z[z<0])
        fig= px.scatter(x=mx,y=my,color=p0[z<0]/(5/6))
        fig.update_yaxes(scaleanchor = "x", scaleratio = 1)
        fig.write_image(fig_path+"_1"+fig_format) 
        
        
        
        mx=x[z>0]/(z[z>0]+1)
        my=y[z>0]/(z[z>0]+1)
        fig= px.scatter(x=mx,y=my,color=p0[z>0]/(5/6))
        
        fig.update_yaxes(scaleanchor = "x", scaleratio = 1)
        fig.write_image(fig_path+"_2"+fig_format) 
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