from function_plotting import *
import mpl_toolkits.mplot3d.axes3d as axes3d
from matplotlib import cm
from matplotlib import colors

if __name__=="__main__":
    # if we keep 0 and pi some visual artifacts might appear

    fig_title = "Rotated Economical Phase Covariant QCM\nIdeal (3D)\n"
    fig_save = "rotated_economical_phase_covariant_3D.png"
    fidelity_f = economical_phase_covariant_fidelity_rotated


    #
    theta = np.linspace(0.01, np.pi - 0.01, 300)
    phi = np.linspace(0, 2 * np.pi, 300)

    # modify phi so that it belongs to [-pi,pi], but keep phi=0 fixed (longitude goes from -180 to +180)
    for i in range(len(phi)):
        if phi[i] >= np.pi:
            phi[i] = -np.pi + phi[i] % np.pi

    theta, phi = np.meshgrid(theta, phi)
    p0_1_ideal = fidelity_f(theta, phi)
    
    R = 1
    X = R * np.sin(phi) * np.cos(theta)
    Y = R * np.sin(phi) * np.sin(theta)
    Z = R * np.cos(phi)
    # Plot the ideal fidelity using the Mollweide projection of the sphere

    fig = plt.figure(figsize=plt.figaspect(0.5)*1.5)
    ax = fig.gca(projection="3d")
    ax.set_box_aspect((1, 1, 0.86)) 
    ax.grid(True)
    ax.tick_params(axis='x', colors='white')



    cmap = plt.get_cmap('plasma')
    # # Only keep the darker colors, so we can use white for the central labels
    new_cmap = truncate_colormap(cmap, 0, 0.9)
    
    color_dimension = p0_1_ideal # change to desired fourth dimension
    minn, maxx = color_dimension.min(), color_dimension.max()
    norm = colors.Normalize(minn, maxx)
    m = plt.cm.ScalarMappable(norm=norm, cmap=new_cmap)
    m.set_array([])
    fcolors = m.to_rgba(color_dimension)
    
    surf = ax.plot_surface(X, Y, Z, cmap=new_cmap, facecolors=fcolors,alpha=1,
                       linewidth=0)
    # sc = ax.scatter(phi, np.pi / 2 - theta, c=p0_1_ideal, lw=0, s=3, alpha=1, cmap=new_cmap)
    cbar = plt.colorbar(surf, orientation="horizontal", fraction=0.046, pad=0.04)


    cbar.set_label('Fidelity')
    plt.title(fig_title)
    plt.savefig(fig_save, dpi=300)

    plt.show()