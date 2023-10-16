#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Import necessary packages
import pyvista as pv
import pyvistaqt as pvqt
import numpy as np
import PVGeo
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
from matplotlib.colors import ListedColormap
from scipy.stats import entropy

import matplotlib as mpl

mpl.rcParams["figure.dpi"] = 500

# pv.set_plot_theme("dark")


# In[ ]:


ALLOWED_SHEETS = [
    "LITHOLOGY",
    #'SAMPLE',
    #'WELL LOG',
    "WC DENSITY",
    "ATTB READINGS",
    "HYD READINGS",
    "SV READINGS",
]

# Below is the color bar for the 8 ESUs encountered in CI project along with the associated color code
ESU_COLORS = {
    "FILL": "#ddb892",
    "RS": "#c9184a",
    "KA": "#ffba08",
    "AVFB": "#3d405b",
    "AVFT": "#6da5dd",
    "ECBF": "#5f0f40",
    "PVC": "#0b525b",
    "TG": "#2a9d8f",
}

ESU_COLORMAP = ListedColormap(
    [pv.Color(color).float_rgba for color in ESU_COLORS.values()]
)


TW_COLORS = {
    "0-30%": "#28A428",
    "30-50%": "#FFEA00",
    ">70%": "#FF0000",
}

TW_COLORMAP = ListedColormap(
    [pv.Color(color).float_rgba for color in TW_COLORS.values()]
)

GMP_COLORS = {
    "Alarm": "#28A428",
    "Alert": "#FFEA00",
    "Normal": "#FF0000",
}

GMP_COLORMAP = ListedColormap(
    [pv.Color(color).float_rgba for color in GMP_COLORS.values()]
)


def points_to_poly_data(points_df, spat_ref=None):
    if spat_ref is None:
        # Assume first three columns
        spat_ref = points_df.keys()[:3]
    poly = pv.PolyData(points_df[spat_ref].values)
    poly.point_data.update(points_df.to_dict(orient="list"))
    return poly


def polyline_from_points(points):
    if isinstance(points, pv.PolyData):
        data = points.point_data
        points = points.points
    else:
        data = {}
    poly = pv.PolyData()
    poly.points = points
    the_cell = np.arange(0, len(points), dtype=np.int_)
    the_cell = np.insert(the_cell, 0, len(points))
    poly.lines = the_cell
    poly.point_data.update(data)
    return poly


def decompose_wells(wpdi):
    # Get number of points
    composite = pv.MultiBlock()
    #### Perfrom task ####
    # Get the Points over the NumPy interface
    pts = wpdi.points
    # TODO: get data:
    keys = wpdi.array_names
    data = dict()
    for k in keys:
        arr = wpdi[k]
        data.setdefault(k, arr)
    collars, blockids = np.unique(pts[:, 0:2], return_inverse=True, axis=0)
    for blk, collar in enumerate(collars):
        well = pts[blockids == blk]
        # Now get data values
        df = pd.DataFrame(data=well, columns=["X", "Y", "Z"])
        for k in data.keys():
            df[k] = data[k][blockids == blk]
        poly = points_to_poly_data(df)
        line = polyline_from_points(poly.points)
        line.point_data.update(poly.point_data)
        composite.append(line)
    return composite



def bind_to_plotter(plotter):

    tunnel_var = pd.read_csv("data/Final-DTA.csv")
    tunnel_var.tail()


    # In[ ]:


    # Select very 50th ring for labels
    ring_sel = tunnel_var[tunnel_var.index % 50 == 0]
    ring_sel = ring_sel[["Easting", "Northing", "Tun-Elevation"]]
    ring_sel
    ring_sel = ring_sel.to_numpy()
    ring_sel
    end_ring_sel = ring_sel.copy()
    end_ring_sel[:, 2] -= 50


    # In[ ]:


    line_ring = np.concatenate((ring_sel, end_ring_sel), axis=1).reshape(
        (-1, 3)
    )  # from six columns to three columns, start and end on consecutive rows


    # In[ ]:


    vertices = line_ring
    lines = []
    for i in range(len(vertices) // 2):
        lines.append([2, i * 2, i * 2 + 1])
    ring_label_mesh = pv.PolyData(vertices, lines=lines)
    ring_labels = pv.PolyData(end_ring_sel)
    ring_labels["Ring Labels"] = [f"R-{i*50}" for i in range(ring_labels.n_points)]


    # In[ ]:


    spat_ref = ["Easting", "Northing", "Tun-Elevation"]
    tunnel_ring_pts = pv.PolyData(tunnel_var[spat_ref].values)
    tunnel_ch_pts = pv.PolyData(tunnel_var[spat_ref].values)
    tunnel_ring_pts["Ring"] = tunnel_var["Ring"].values
    tunnel_ch_pts["Chainage"] = tunnel_var["Chainage"].values
    # Make tubes/tunnels
    r = 19
    tunnel_ci_ring = polyline_from_points(tunnel_ring_pts).tube(radius=r)
    tunnel_ci_ch = polyline_from_points(tunnel_ch_pts).tube(radius=r)


    # In[ ]:


    tunnel_ci_path = polyline_from_points(tunnel_ring_pts)
    r = 10
    tunnel_ci = tunnel_ci_path.tube(radius=r)
    spline = pv.Spline(tunnel_ci_path.points, n_points=100)
    # geo_profile = geo_sim.slice_along_line(spline)


    # # Add Real-Time Tunnel Boring Machine Data

    # In[ ]:


    tbm_data_1 = pd.read_csv(
        "data/CI Main Tunnel_Rajat-Output_2021-08-12_2021-11-25.csv", sep=";"
    )
    tbm_data_2 = pd.read_csv(
        "data/CI Main Tunnel_Rajat-Output_2021-11-25_2021-12-24.csv", sep=";"
    )
    tbm_data_3 = pd.read_csv("data/CI Main Tunnel_Rajat-Output_ring_226_to_274.csv", sep=";")


    # In[ ]:


    tbm_data = pd.concat([tbm_data_1, tbm_data_2, tbm_data_3], ignore_index=True)
    # Convert Timestamp colume to DateTime
    tbm_data["Timestamp"] = pd.to_datetime(tbm_data["Timestamp"])
    tbm_data = tbm_data[tbm_data["Ring"] >= 1]
    tbm_data = tbm_data[
        (tbm_data["QDV_Excavation_chamber_pressure_02"] <= 10)
        & (tbm_data["QDV_Excavation_chamber_pressure_02"] > 0)
    ]
    tbm_data_mean = tbm_data.groupby(["Ring"]).mean().reset_index()
    tbm_data_mean = tbm_data_mean.drop("Unnamed: 14", axis=1)
    tbm_data_mean = tbm_data_mean.drop("QDV_Drill_rig_01_rotation_speed", axis=1)
    # tbm_data_mean = tbm_data_mean.drop('Ring', 1)
    tbm_data_mean.columns = tbm_data_mean.columns.str.replace(r"QDV_", "")
    tbm_data_mean["Advance_thrust_force"] = tbm_data_mean["Advance_thrust_force"] / 10
    tbm_data_mean = tbm_data_mean.round(2)
    tbm_data_mean = pd.merge(tbm_data_mean, tunnel_var, on=["Ring"], how="left")
    tbm_data_mean = tbm_data_mean.dropna(axis="rows")
    # tbm_data_mean = tbm_data_mean[tbm_data_mean['Ring'] < 225]


    # In[ ]:


    spat_ref = ["Easting", "Northing", "Tun-Elevation"]
    tunnel_tbm_pts = pv.PolyData(tbm_data_mean[spat_ref].values)

    tunnel_tbm_pts["Ring"] = tbm_data_mean["Ring"].values
    tunnel_tbm_pts["PR"] = tbm_data_mean["Penetration"].values
    tunnel_tbm_pts["AR"] = tbm_data_mean["Advance_speed"].values
    tunnel_tbm_pts["EP"] = tbm_data_mean["Excavation_chamber_pressure_02"].values
    tunnel_tbm_pts["Torque"] = tbm_data_mean["Main_drive_torque"].values
    tunnel_tbm_pts["Thrust"] = tbm_data_mean["Advance_thrust_force"].values

    # # Make tubes/tunnels
    tunnel_ci_tbm = polyline_from_points(tunnel_tbm_pts).tube(radius=20)


    # In[ ]:


    array_advance = "AR"
    array_penetration = "PR"
    array_torque = "Torque"
    array_thrust = "Thrust"
    array_pressure = "EP"
    ring_id = "Ring"


    # # Add Digital Elevation Model

    # In[ ]:


    ground_surf = tunnel_var[["Easting", "Northing", "Ground-Elevation"]]
    ground_surf = ground_surf.to_numpy()


    # In[ ]:


    # sargs2 = dict(height=0.25, vertical=True, position_x=0.05, position_y=0.95, title_font_size = 30, label_font_size=15)
    # plotter = pv.Plotter(title="ARUP-Geotechnical Information Visualization and Analyses (GIVA)")
    # plotter.add_mesh(tunnel_ci_ring, color='white')
    # plotter.add_mesh(ring_label_mesh.tube(radius=1.2), color='white')
    # plotter.add_lines(ground_surf,color="red",width=3)
    # plotter.enable_point_picking(callback=callback, show_message=True,color='pink', point_size=20,use_mesh=True, show_point=True)


    # In[ ]:


    dem = pd.read_csv("data/dem.csv")
    dem2 = pd.read_csv("data/dem2.csv")
    dem_sel = dem[
        dem.index % 100 == 0
    ]  # reading every 100th row as the file is pretty heavy
    dem2_sel = dem2[
        dem2.index % 100 == 0
    ]  # reading every 100th row as the file is pretty heavy
    spat_ref = ["Easting", "Northing", "Elevation"]
    dem_sel_cloud = pv.PolyData(dem_sel[spat_ref].values)
    dem2_sel_cloud = pv.PolyData(dem2_sel[spat_ref].values)


    # # Add Geotechnical Data

    # In[ ]:


    bh = pd.read_csv("data/CI-Boreholes.csv")
    spt = pd.read_csv("data/CI-N160.csv")
    att = pd.read_csv("data/CI-Atterberg.csv")
    bh_df = pd.read_csv("data/CI-Geology-Updated.csv", encoding="unicode_escape")


    # In[ ]:


    bh_df = bh_df.drop(["GEOL_DESC", "GEOL_STAT", "GEOL_LEG"], axis=1)
    bh_geol = pd.merge(
        bh_df,
        bh[["Easting", "Northing", "Elevation", "Final Depth (m)", "Borehole"]],
        left_on="PointID",
        right_on="Borehole",
        how="left",
    )
    # bh_geol['SE'] = bh_geol['Elevation']-bh_geol['Depth']
    bh_geol = bh_geol.dropna()
    bh_geol = bh_geol[
        bh_geol["PointID"].str.contains(
            "CPT|DMT|AS|WWTP|L3S|HA|WS3|MH|NZ63948_BH58|NZ63956_BH66|NZ101929_TP4|NZ101930_TP5"
        )
        == False
    ]
    bh_geol.drop_duplicates(inplace=True)
    bh_geol.head()


    # In[ ]:


    g = bh_geol.groupby("PointID", as_index=False).last()
    g["Depth"] = g["GEOL_BASE"]
    g.head()

    bh_new_geol = pd.concat([bh_geol, g])
    bh_new_geol.sort_values(by=["PointID", "Depth"], inplace=True)
    bh_new_geol.reset_index()
    bh_new_geol.head(65)
    bh_new_geol["SE"] = bh_new_geol["Elevation"] - bh_new_geol["Depth"]
    bh_new_geol.head(65)

    bh_new_geol.to_csv("BH-Modeling.csv")


    # In[ ]:


    # bh_df = bh_df.dropna()
    bh_new_geol.drop_duplicates(
        subset=["PointID", "Depth", "Easting", "Northing", "SE"], keep="last"
    )
    post_idx = bh_new_geol[np.isclose(bh_new_geol["Depth"].diff(), 0)].index
    pre_idx = post_idx.copy() - 1
    same_depth = np.hstack([pre_idx, post_idx])
    same_depth.sort()
    bh_new_geol.loc[same_depth]


    # In[ ]:


    spat_ref = ["Easting", "Northing", "SE"]
    bh_pts = pv.PolyData(bh_new_geol[spat_ref].values)
    bh_pts.point_data.update(bh_new_geol.to_dict(orient="list"))
    decomp = decompose_wells(bh_pts)
    bh_lines = decomp.combine().extract_geometry()
    boreholes = bh_lines.tube(radius=20)


    # In[ ]:


    bh["Bottom Elevation"] = bh["Elevation"] - bh["Final Depth (m)"]
    bh_start = bh[["Easting", "Northing", "Elevation"]]
    bh_start = bh_start.to_numpy()
    bh_end = bh[["Easting", "Northing", "Bottom Elevation"]]
    bh_end = bh_end.to_numpy()
    bh_line = np.concatenate((bh_start, bh_end), axis=1).reshape((-1, 3))
    # from six columns to three columns, start and end on consecutive rows
    vertices = bh_line
    lines = []
    for i in range(len(vertices) // 2):
        lines.append([2, i * 2, i * 2 + 1])
    bh_tube = pv.PolyData(vertices, lines=lines)

    bh_labels = pv.PolyData(bh_start)
    bh_labels["Borehole Labels"] = bh["Borehole"]


    # In[ ]:


    # pl = pv.Plotter()
    # sargs = dict(
    #     height=0.25,
    #     vertical=True,
    #     position_x=0.07,
    #     position_y=0.05,
    #     title_font_size=30,
    #     label_font_size=30,
    # )
    # pl.add_mesh(boreholes, cmap=ESU_COLORMAP, scalars="Unit", scalar_bar_args=sargs)
    # pl.show()


    # # Continuous Geotechnical Data

    # ## SPT Data

    # In[ ]:


    spt = pd.read_csv("data/CI-N160.csv")
    spt.head()


    # In[ ]:


    spt["Start Elevation"] = spt["Elevation"] - spt["ISPT_DPTH"]
    spt["End Elevation"] = spt["Elevation"] - spt["Depth"]
    spt_start = spt[["Easting", "Northing", "Start Elevation"]]
    spt_start = spt_start.to_numpy()
    spt_end = spt[["Easting", "Northing", "End Elevation"]]
    spt_end = spt_end.to_numpy()
    spt_line = np.concatenate((spt_start, spt_end), axis=1).reshape((-1, 3))
    # #from six columns to three columns, start and end on consecutive rows
    vertices = spt_line
    lines = []
    for i in range(len(vertices) // 2):
        lines.append([2, i * 2, i * 2 + 1])
    spt_tube = pv.PolyData(vertices, lines=lines)
    spt_tube["SPT"] = spt["N1_60"]
    spt_tube


    # In[ ]:


    # pl = pv.Plotter()
    # # pl.add_mesh(tunnel_ci_ring, color='white')
    # pl.add_mesh(spt_tube.tube(radius=20), scalars="SPT", cmap="seismic")
    # pl.add_mesh(bh_tube.tube(radius=10), color="white")
    # # pl.add_mesh(geo_sim, opacity=0.2, show_scalar_bar=True,lighting=True,cmap='seismic',scalars='Mean-SPT')
    # pl.show()


    # In[ ]:


    spt_stats = pd.read_csv("data/N160-SGS-Stats.csv")
    spt_stats.head()


    # In[ ]:


    spat_ref1 = ["Easting", "Northing", "Elevation"]
    # Create the points
    geo_sim_spt_pts = points_to_poly_data(spt_stats, spat_ref1)
    # Voxelize the points
    geo_sim_spt = PVGeo.filters.VoxelizePoints().apply(geo_sim_spt_pts)


    # In[ ]:


    # geo_sim_spt_pts.plot(scalars="Mean-SPT")


    # ## ECBF Elevation Uncertainty

    # In[ ]:


    ecbf_stats = pd.read_csv("data/ECBF-SGS-Stats.csv")
    ecbf_stats.head()


    # In[ ]:


    spat_ecbf = ["Easting", "Northing", "Mean-Elevation"]
    geo_sim_ecbf_pts = points_to_poly_data(ecbf_stats, spat_ecbf)
    # Voxelize the points
    # geo_sim_ecbf = PVGeo.filters.VoxelizePoints().apply(geo_sim_ecbf_pts)
    geo_sim_ecbf_pts


    # # Geostatistical Modeling Output

    # In[ ]:


    # This comes from the R Scripts for modeling
    a = pd.read_csv("data/CI-GeolModel.csv")
    a.drop("Class", axis=1, inplace=True)
    a.head()


    # In[ ]:


    # Caluclating uncertainty
    entropy_cols = [col for col in a.columns if "Macro" in col]
    a_unc = a[entropy_cols]
    a_unc["E"] = entropy(a_unc[entropy_cols], base=10, axis=1)
    a_unc.tail()
    # a_unc.head()
    a["E"] = a_unc["E"]
    a.head()


    # In[ ]:


    ref = ["Easting", "Northing", "Elevation"]
    geo_sim_pts = points_to_poly_data(a, ref)
    geo_sim = PVGeo.filters.VoxelizePoints().apply(geo_sim_pts)
    geo_profile = geo_sim.slice_along_line(spline)


    # In[ ]:


    # pl=pv.Plotter()
    # # pl.add_mesh(boreholes, cmap=ESU_COLORMAP,scalars='Unit',scalar_bar_args=sargs)
    # pl.add_mesh(geo_profile, cmap=ESU_COLORMAP,scalars='MP',scalar_bar_args=sargs)
    # # pl.add_mesh(geo_sim, opacity=0.8, show_scalar_bar=False,lighting=True,cmap=ESU_COLORMAP,scalars='MP')
    # # pl.add_mesh(geo_sim, opacity=0.8, show_scalar_bar=True,lighting=True,cmap='seismic',scalars='E',scalar_bar_args={"title": "Uncertainty"})
    # #pl.add_mesh(slices)
    # pl.show()


    # # Visualization

    # In[ ]:


    # 3D Interactive Rendering Window of Central Interceptor Excavation Environment
    # plotter = pvqt.BackgroundPlotter(
    #     title="ARUP-Geotechnical Information Visualization and Analyses (GIVA)"
    # )

    # Scalar Bar Configurations
    dargs = dict(scalars="Uncertainty", cmap="seismic", opacity=1.0, clim=[0, 1])

    dargs1 = dict(scalars="Uncertainty", cmap="seismic", opacity=1.0, clim=[0, 1])

    sargs = dict(
        height=0.25,
        vertical=True,
        position_x=0.07,
        position_y=0.05,
        title_font_size=30,
        label_font_size=30,
    )

    sargs1 = dict(
        height=0.25,
        vertical=True,
        position_x=0.85,
        position_y=0.05,
        title_font_size=30,
        label_font_size=14,
    )

    sargs2 = dict(
        height=0.25,
        vertical=True,
        position_x=0.05,
        position_y=0.95,
        title_font_size=30,
        label_font_size=15,
    )

    sargs3 = dict(
        height=0.25,
        vertical=True,
        position_x=0.85,
        position_y=0.95,
        title_font_size=30,
        label_font_size=5,
        n_labels=0,
    )

    dargs = dict(name="labels", font_size=40)

    cmap_spt = plt.cm.autumn
    cmap_reversed = plt.cm.get_cmap("autumn_r")


    def callback_penetration(mesh, pid):
        point = tunnel_ci_tbm.points[pid]
        label = [
            "Ring: {}\n{}: {}".format(
                tunnel_ci_tbm[ring_id][pid],
                array_penetration,
                tunnel_ci_tbm[array_penetration][pid],
            )
        ]
        plotter.add_point_labels(point, label, **dargs)


    def callback_advance(mesh, pid):
        point = tunnel_ci_tbm.points[pid]
        label = [
            "Ring: {}\n{}: {}".format(
                tunnel_ci_tbm[ring_id][pid],
                array_advance,
                tunnel_ci_tbm[array_advance][pid],
            )
        ]
        plotter.add_point_labels(point, label, **dargs)


    def callback_thrust(mesh, pid):
        point = tunnel_ci_tbm.points[pid]
        label = [
            "Ring: {}\n{}: {}".format(
                tunnel_ci_tbm[ring_id][pid], array_thrust, tunnel_ci_tbm[array_thrust][pid]
            )
        ]
        plotter.add_point_labels(point, label, **dargs)


    def callback_torque(mesh, pid):
        point = tunnel_ci_tbm.points[pid]
        label = [
            "Ring: {}\n{}: {}".format(
                tunnel_ci_tbm[ring_id][pid], array_torque, tunnel_ci_tbm[array_torque][pid]
            )
        ]
        plotter.add_point_labels(point, label, **dargs)


    def callback_pressure(mesh, pid):
        point = tunnel_ci_tbm.points[pid]
        label = [
            "Ring: {}\n{}: {}".format(
                tunnel_ci_tbm[ring_id][pid],
                array_pressure,
                tunnel_ci_tbm[array_pressure][pid],
            )
        ]
        plotter.add_point_labels(point, label, **dargs)


    # ************** Start of Button Commands************************


    def add_tunnel_ci():
        plotter.add_mesh(tunnel_ci_ring, color="white", name="Tunnel Alignment")


    user_menu = plotter.main_menu.addMenu("Base Layers")
    user_menu.addAction("Add Tunnel Alignment", add_tunnel_ci)


    def add_ring_markers():
        plotter.add_mesh(ring_label_mesh.tube(radius=1.2), color="white")
        plotter.add_point_labels(ring_labels, "Ring Labels", point_size=3, font_size=12)


    user_menu.addAction("Add Ring Markers", add_ring_markers)


    def add_ground_surface():
        #     plotter.add_lines(ground_surf,color="red",width=3)
        plotter.add_mesh(dem_sel_cloud, color="brown", opacity=0.5)
        plotter.add_mesh(dem2_sel_cloud, color="brown", opacity=0.5)


    user_menu.addAction("Add Ground Surface", add_ground_surface)


    def add_boreholes_labels():
        plotter.add_point_labels(bh_labels, "Borehole Labels", point_size=3, font_size=12)


    user_menu.addAction("Add Borehole Labels", add_boreholes_labels)

    # ********************************************************BLOCK GEOTECHNICAL******************************************
    # def add_bh():
    #     plotter.add_mesh(bh_tube.tube(radius=10), color='white')
    # #     plotter.add_point_labels(bh_labels, "Borehole Labels", point_size=3, font_size=12)
    # geotech_menu = plotter.main_menu.addMenu('Geotechnical Data')
    # geotech_menu.addAction('Show BHs', add_bh)


    def add_geol():
        #     plotter.add_mesh(bh_tube.tube(radius=10), color='white')
        plotter.add_mesh(
            boreholes, cmap=ESU_COLORMAP, scalars="Unit", scalar_bar_args=dict(**sargs, n_labels=8)
        )


    geotech_menu = plotter.main_menu.addMenu("Geotechnical Data")
    geotech_menu.addAction("Add Boreholes", add_geol)


    def add_spt():
        plotter.add_mesh(spt_tube.tube(radius=20), scalars="SPT", cmap=cmap_reversed)
        plotter.add_point_labels(bh_labels, "Borehole Labels", point_size=3, font_size=12)


    geotech_menu.addAction("Show SPTs", add_spt)


    def add_att():
        plotter.add_mesh(bh_tube.tube(radius=10), color="white")
        plotter.add_point_labels(bh_labels, "Borehole Labels", point_size=3, font_size=12)


    AttMenu = geotech_menu.addMenu("Show Atterberg")
    AttMenu.addAction("Show LL")
    AttMenu.addAction("Show PI")

    # ********************************************************BLOCK 3D MODELS******************************************
    # def add_bh():
    #     plotter.add_mesh(bh_tube.tube(radius=10), color='white')
    # #     plotter.add_point_labels(bh_labels, "Borehole Labels", point_size=3, font_size=12)
    # geotech_menu = plotter.main_menu.addMenu('Geotechnical Data')
    # geotech_menu.addAction('Show BHs', add_bh)


    def add_geol_model():
        plotter.add_mesh(
            geo_sim,
            opacity=0.6,
            show_scalar_bar=False,
            lighting=True,
            cmap=ESU_COLORMAP,
            scalars="MP",
        )


    models_menu = plotter.main_menu.addMenu("Stochastic Models")
    models_menu.addAction("Most Probable Model", add_geol_model)


    def add_geol_uncer():
        plotter.add_mesh(
            geo_sim,
            opacity=0.6,
            show_scalar_bar=True,
            lighting=True,
            cmap="seismic",
            scalars="E",
            scalar_bar_args={"title": "Uncertainty"},
        )


    models_menu.addAction("Geological Uncertainty", add_geol_uncer)


    def add_spt_model():
        plotter.add_mesh(geo_sim_spt, cmap="inferno_r", scalars="Mean-SPT")


    models_menu.addAction("Mean SPT Model", add_spt_model)


    def add_spt_25qt():
        plotter.add_mesh(geo_sim_spt, cmap="inferno_r", scalars="SPT-25QT")


    def add_spt_50qt():
        plotter.add_mesh(geo_sim_spt, cmap="inferno_r", scalars="SPT-50QT")


    def add_spt_75qt():
        plotter.add_mesh(geo_sim_spt, cmap="inferno_r", scalars="SPT-75QT")


    def add_spt_sd():
        plotter.add_mesh(geo_sim_spt, cmap="inferno_r", scalars="SD-SPT")


    SPTMenu = models_menu.addMenu("SPT Uncertainty")
    SPTMenu.addAction("SPT SD", add_spt_sd)
    SPTMenu.addAction("SPT 25QT", add_spt_25qt)
    SPTMenu.addAction("SPT 50QT", add_spt_50qt)
    SPTMenu.addAction("SPT 75QT", add_spt_75qt)


    def add_ecbf_model():
        plotter.add_mesh(
            geo_sim_ecbf_pts,
            cmap="inferno_r",
            scalars="Mean_ECBF",
            scalar_bar_args={"title": "ECBF-Mean Elevation (m)"},
        )


    models_menu.addAction("ECBF Mean Elevation", add_ecbf_model)


    def add_ecbf_90():
        plotter.add_mesh(
            geo_sim_ecbf_pts,
            cmap="inferno_r",
            scalars="PI_90",
            scalar_bar_args={"title": "90 PI ECBF Elevation (m)"},
        )


    def add_ecbf_95():
        plotter.add_mesh(
            geo_sim_ecbf_pts,
            cmap="inferno_r",
            scalars="PI_95",
            scalar_bar_args={"title": "95 PI ECBF Elevation (m)"},
        )


    def add_ecbf_sd():
        plotter.add_mesh(geo_sim_ecbf_pts, cmap="inferno_r", scalars="SD-Elevation")


    ECBFMenu = models_menu.addMenu("ECBF Elevation Uncertainty")
    ECBFMenu.addAction("ECBF Elevation SD", add_ecbf_sd)
    ECBFMenu.addAction("90 PI ECBF Elevation", add_ecbf_90)
    ECBFMenu.addAction("95 PI ECBF Elevation", add_ecbf_95)

    # ********************************************************2D Profiles**************************************************
    from PVGeo.filters import ManySlicesAlongPoints

    slices_spt = ManySlicesAlongPoints(n_slices=50).apply(tunnel_ring_pts, geo_sim_spt)
    slices_geol = ManySlicesAlongPoints(n_slices=50).apply(tunnel_ring_pts, geo_sim)


    def add_geol_profile():
        plotter.add_mesh(
            geo_profile,
            opacity=0.6,
            show_scalar_bar=False,
            lighting=True,
            cmap=ESU_COLORMAP,
            scalars="MP",
        )


    models_menu = plotter.main_menu.addMenu("Profiles")
    models_menu.addAction("Most Probable Profile", add_geol_profile)


    def add_uncer_profile():
        plotter.add_mesh(
            geo_profile,
            opacity=0.6,
            show_scalar_bar=False,
            lighting=True,
            cmap="seismic",
            scalars="E",
        )


    models_menu.addAction("Uncertainty Profile", add_uncer_profile)


    def add_geol_slices():
        plotter.add_mesh(
            slices_geol, cmap=ESU_COLORMAP, scalars="MP", show_scalar_bar=False
        )


    models_menu.addAction("Transverse Profiles (Geology)", add_geol_slices)


    def add_uncer_slices():
        plotter.add_mesh(
            slices_geol,
            cmap="seismic",
            scalars="E",
            scalar_bar_args={"title": "Uncertainty"},
            show_scalar_bar=True,
            lighting=True,
        )


    models_menu.addAction("Transverse Profiles (Uncertainty)", add_uncer_slices)


    def add_spt_slices():
        plotter.add_mesh(slices_spt, cmap="inferno_r", scalars="Mean-SPT")


    models_menu.addAction("Transverse Profiles (SPT)", add_spt_slices)


    # ********************************************************BLOCK TBM**************************************************
    def add_rop():
        plotter.add_mesh(
            tunnel_ci_tbm,
            scalars="PR",
            show_scalar_bar=True,
            cmap="viridis_r",
            scalar_bar_args={"title": "PR (mm/rot)"},
            name="Penetration",
        )
        # plotter.enable_point_picking(
        #     callback=callback_penetration,
        #     show_message=True,
        #     color="pink",
        #     point_size=20,
        #     use_mesh=True,
        #     show_point=True,
        # )


    tbm_menu = plotter.main_menu.addMenu("TBM Parameters")
    tbm_menu.addAction("Add Penetration", add_rop)


    def add_advance():
        plotter.add_mesh(
            tunnel_ci_tbm,
            scalars="AR",
            show_scalar_bar=True,
            cmap="inferno_r",
            scalar_bar_args={"title": "Advance Rate (mm/min)"},
            name="Advance Rate",
        )
        # plotter.enable_point_picking(
        #     callback=callback_advance,
        #     show_message=True,
        #     color="pink",
        #     point_size=20,
        #     use_mesh=True,
        #     show_point=True,
        # )


    tbm_menu.addAction("Add Advance Rate", add_advance)


    def add_chamber():
        plotter.add_mesh(
            tunnel_ci_tbm,
            scalars="EP",
            show_scalar_bar=True,
            cmap="inferno_r",
            scalar_bar_args={"title": "Chamber Pressure (bar)"},
            name="Chamber Pressure",
        )
        # plotter.enable_point_picking(
        #     callback=callback_pressure,
        #     show_message=True,
        #     color="pink",
        #     point_size=20,
        #     use_mesh=True,
        #     show_point=True,
        # )


    tbm_menu.addAction("Add Chamber Pressure", add_chamber)


    def add_thrust():
        plotter.add_mesh(
            tunnel_ci_tbm,
            scalars="Thrust",
            show_scalar_bar=True,
            cmap="inferno_r",
            scalar_bar_args={"title": "Thrust Force (MN)"},
            name="Thrust Force",
        )
        # plotter.enable_point_picking(
        #     callback=callback_thrust,
        #     show_message=True,
        #     color="pink",
        #     point_size=20,
        #     use_mesh=True,
        #     show_point=True,
        # )


    tbm_menu.addAction("Add Thrust Force", add_thrust)


    def add_torque():
        plotter.add_mesh(
            tunnel_ci_tbm,
            scalars="Torque",
            show_scalar_bar=True,
            cmap="inferno_r",
            scalar_bar_args={"title": "Cutterhead Torque (MNm)"},
            name="Cutterhead Torque",
        )
        # plotter.enable_point_picking(
        #     callback=callback_torque,
        #     show_message=True,
        #     color="pink",
        #     point_size=20,
        #     use_mesh=True,
        #     show_point=True,
        # )


    tbm_menu.addAction("Add Torque", add_torque)


    def add_tbmplots():
        # get_ipython().run_line_magic('matplotlib', 'qt')

        fig, axs = plt.subplots(5, sharex=True)
        axs[0].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Excavation_chamber_pressure_01"],
            color="#e63946",
            label="EP1",
        )
        axs[0].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Excavation_chamber_pressure_02"],
            color="#264653",
            label="EP2",
        )
        axs[0].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Excavation_chamber_pressure_03"],
            color="#f4a261",
            label="EP3",
        )
        axs[0].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Excavation_chamber_pressure_04"],
            color="#2a9d8f",
            label="EP4",
        )
        axs[0].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Excavation_chamber_pressure_05"],
            color="#7209b7",
            label="EP5",
        )
        axs[0].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Excavation_chamber_pressure_06"],
            color="#bc6c25",
            label="EP6",
        )
        axs[0].xaxis.set_major_locator(MultipleLocator(20))
        axs[0].xaxis.set_minor_locator(MultipleLocator(1))
        axs[0].set_xlabel(" ")
        axs[0].set_ylabel("Chamber Pr.(bar)")
        axs[0].grid(True)

        axs[1].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Advance_speed"],
            color="#e63946",
            label="AR",
            linewidth=2,
            marker="o",
        )
        axs[1].set_ylabel("AR (mm/min)")
        axs[1].grid(True)

        axs[2].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Penetration"],
            color="#003049",
            label="Pr",
            linewidth=2,
            marker="o",
        )
        axs[2].set_ylabel("Pr (mm/rev)")
        axs[2].grid(True)

        axs[3].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Main_drive_torque"],
            color="#FF0000",
            label="Torque",
            linewidth=2,
            marker="o",
        )
        axs[3].set_ylabel("Torque(MNm)")
        axs[3].grid(True)

        axs[4].plot(
            tbm_data_mean["Ring"],
            tbm_data_mean["Advance_thrust_force"],
            color="#FF00B6",
            label="Thrust",
            linewidth=2,
            marker="o",
        )
        axs[4].set_ylabel("Thrust(MN)")
        axs[4].grid(True)
        fig.tight_layout()


    tbm_menu.addAction("Mean TBM Parameters", add_tbmplots)


# In[ ]:
