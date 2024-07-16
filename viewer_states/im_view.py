import hou
import viewerstate.utils as su
import pprint


class State(object):
    HUD_TEMPLATE = {
        "title": "IM View",
        "rows":\
        [
            {"id": "projection", "label": "Projection:", "value": "Orthographic"},
            {"id": "pivot_style", "label": "Pivot Style:", "value": "Origin"},
            {"id": "movement_style", "label": "Movement Style:",
                "value": "Rotate", "key": "M"},
            {"id": "xform", "label": "Xform", "key": "H/J/K/L"}
        ]
    }

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.viewer = scene_viewer
        self.reset = 1

        # Drawables
        self.axis_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="axis_drawable",
            params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        self.axis_drawable.show(True)

        self.pivot_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="pivot_drawable")
        self.pivot_drawable.show(True)

        self.ray_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="ray_drawable")
        self.ray_drawable.show(True)

    ##

    def get_centroid(self):
        return

    def get_xform(self):
        t = self.state_parms["t"]["value"]
        r = self.state_parms["r"]["value"]
        print(self.state_parms["p"]["value"])
        p = self.state_parms["p"]["value"]
        pr = self.state_parms["pr"]["value"]
        return(t, r, p, pr)

    def handle_rotate(self, key):
        r = list(self.state_parms["r"]["value"])
        r_scale = self.state_parms["r_scale"]["value"]
        if key == "h":
            r[1] = (r[1] + r_scale) % 360
        elif key == "j":
            r[0] = (r[0] - r_scale) % 360
        elif key == "k":
            r[0] = (r[0] + r_scale) % 360
        elif key == "l":
            r[1] = (r[1] - r_scale) % 360
        self.state_parms["r"]["value"] = r
        self.update_cam()

    def handle_translate(self, key):
        t = list(self.state_parms["t"]["value"])
        t_scale = self.state_parms["t_scale"]["value"]
        if key == "h":
            t[0] -= t_scale
        elif key == "j":
            t[1] -= t_scale
        elif key == "k":
            t[1] += t_scale
        elif key == "l":
            t[0] += t_scale
        self.state_parms["t"]["value"] = t
        self.update_cam()

    def handle_xform(self, key):
        movement_style = "rotate"
        if self.state_parms["movement_style"]["value"]:
            movement_style = "translate"
        eval("self.handle_" + movement_style + "(key)")
        self.update_pivot_drawable()
        self.update_ray_drawable()

    def handle_zoom(self, key):
        zoom_scale = self.state_parms["zoom_scale"]["value"]
        if self.state_parms["projection"]["value"] == "orthographic":
            if key == "-": self.state_parms["ortho_width"]["value"] += zoom_scale
            elif key == "=": self.state_parms["ortho_width"]["value"] -= zoom_scale
        else:
            x=1
        self.update_cam()
        self.update_pivot_drawable()

    def pivot_to_origin(self):
        self.state_parms["p"]["value"] = [0, 0, 0]
        self.cam.parmTuple("t").set((0, 0, 0))

    def print_cam_vals(self):
        t, r, p, pr = self.get_xform()
        print("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", pr)

    def print_kwargs(self, kwargs):
        ui_event = str(kwargs["ui_event"])
        ui_event = ui_event.replace("\\n", "\n")
        del kwargs["ui_event"]
        print("\n")
        pprint.pprint(kwargs)
        print(ui_event)

    def refit_ui(self):
        self.cam.parm("resx").set(1000)
        self.cam.parm("resy").set(1000)
        size = self.viewport.size()
        ratio = size[2] / size[3]
        self.cam.parm("aspect").set(ratio)

    def reset_view(self):
        self.state_parms["t"]["value"] = [0, 0, 4]
        self.state_parms["r"]["value"] = [45, 45, 0]
        self.state_parms["p"]["value"] = [0, 0, -4]
        self.state_parms["pr"]["value"] = [0, 0, 0]
        self.state_parms["ortho_width"]["value"] = 10
        self.update_cam()
        self.update_pivot_drawable()

    def set_cam(self):
        cam_exists = 0
        for node in hou.node("/obj").children():
            if node.name() == "im_cam":
                cam_exists = 1
        if cam_exists == 0:
            cam = hou.node("/obj").createNode("cam")
            cam.setName("im_cam")
        self.cam = hou.node("/obj/im_cam")
        self.viewport.setCamera(self.cam)
        self.viewport.lockCameraToView(True)
        self.state_parms["projection"]["value"] = "orthographic"

    def set_projection(self, projection):
        print(projection)
        if projection == "perspective":
            self.state_parms["projection"]["value"] = "perspective"
        elif projection == "orthographic":
            self.state_parms["projection"]["value"] = "orthographic"

    def set_zoom_scale(self, key):
        if key == "Shift+-":
            self.state_parms["zoom_scale"]["value"] -= 1
        elif key == "Shift+=":
            self.state_parms["zoom_scale"]["value"] += 1

    def state_to_cam(self):
        x=1

    def cam_to_state(self):
        t = self.cam.parmTuple("t").eval()
        p = self.cam.parmTuple("p").eval()
        r = self.cam.parmTuple("r").eval()
        pr = self.cam.parmTuple("pr").eval()
        self.state_parms["t"]["value"] = list(t)
        self.state_parms["p"]["value"] = list(p)
        self.state_parms["r"]["value"] = list(r)
        self.state_parms["pr"]["value"] = list(pr)

    def toggle_movement_style(self):
        movement_style = self.state_parms["movement_style"]["value"]
        movement_style = (movement_style + 1) % 2
        self.state_parms["movement_style"]["value"] = movement_style

    def update_cam(self):
        t, r, p, pr = self.get_xform()
        self.cam.parmTuple("r").set(r)
        self.cam.parmTuple("t").set(t)
        self.cam.parmTuple("p").set(p)
        self.cam.parmTuple("pr").set(pr)
        if self.state_parms["projection"]["value"] == "orthographic":
            self.cam.parm("projection").set(1)
        else:
            self.cam.parm("projection").set(0)
        self.cam.parm("orthowidth").set(self.state_parms["ortho_width"]["value"])

    def update_hud(self):
        movement_style = ("Rotate", "Translate")\
            [self.state_parms["movement_style"]["value"]]
        updates = {
            "movement_style": {"value": movement_style}
        }
        self.viewer.hudInfo(hud_values=updates)

    def update_axis_drawable(self):
        axes = (self.state_parms["x_axis"]["value"],
            self.state_parms["y_axis"]["value"],
            self.state_parms["z_axis"]["value"])
        axis_scale = self.state_parms["axis_scale"]["value"]
        geo = hou.Geometry()
        geo.addAttrib(hou.attribType.Point, "Cd", (1, 1, 1))
        for idx in (0, 1, 2):
            if axes[idx]:
                p0 = [0, 0, 0]
                p1 = [0, 0, 0]
                p0[idx] = -axis_scale
                p1[idx] = axis_scale
                pts = geo.createPoints((p0, p1))
                cd = [0, 0, 0]
                cd[idx] = 1
                pts[0].setAttribValue("Cd", cd)
                pts[1].setAttribValue("Cd", cd)
                prim = geo.createPolygon(is_closed=False)
                prim.addVertex(pts[0])
                prim.addVertex(pts[1])
        self.axis_drawable.setGeometry(geo)
        self.axis_drawable.setParams({"fade_factor": 0.0})

    def update_pivot_drawable(self):
        r = list(self.state_parms["r"]["value"])
        t = list(self.state_parms["t"]["value"])
        p = list(self.state_parms["p"]["value"])
        ortho_width = self.state_parms["ortho_width"]["value"]
        s = ortho_width / 2
        pos = hou.Vector3(p) + hou.Vector3(t)
        geo = hou.Geometry()
        circle_verb = hou.sopNodeTypeCategory().nodeVerb("circle")
        circle_verb.setParms({"scale": 1.0, "type": 1, "r": r, "t": pos,
            "scale": s * 0.025})
        circle_verb.execute(geo, [])
        self.pivot_drawable.setGeometry(geo)
        self.pivot_drawable.setParams({
            "color1": hou.Vector4(1, 0, 0, 1),
            "fade_factor": 1.0
        })

    def update_ray_drawable(self):
        t, r, p, pr = self.get_xform()
        geo = hou.Geometry()

        cam_p = hou.Vector3(t)
        cam_r = hou.hmath.buildRotate(r)
        cam_p = cam_p * cam_r
        cam_pt = geo.createPoint()
        cam_pt.setPosition(cam_p)

        pivot_p = hou.Vector3(t) + hou.Vector3(p)
        pivot_pt = geo.createPoint()
        pivot_pt.setPosition(pivot_p)

        prim = geo.createPolygon()
        prim.addVertex(cam_pt)
        prim.addVertex(pivot_pt)
        self.ray_drawable.setGeometry(geo)

    def view_frame(self):
        self.viewport.frameAll()

    def view_home(self):
        self.viewport.home()

    ##
    ##

    def onDraw(self, kwargs):
        self.axis_drawable.draw(kwargs["draw_handle"], {})
        self.pivot_drawable.draw(kwargs["draw_handle"], {})
        self.ray_drawable.draw(kwargs["draw_handle"], {})

    def onGenerate(self, kwargs):
        kwargs["state_flags"]["exit_on_node_select"] = False
        self.viewport = self.viewer.selectedViewport()
        self.state_parms = kwargs["state_parms"]
        self.set_cam()
        self.refit_ui()
        self.update_axis_drawable()
        self.viewer.hudInfo(template=self.HUD_TEMPLATE)
        self.cam_to_state()
        self.update_cam()
        self.update_pivot_drawable()
        self.update_ray_drawable()

    def onKeyEvent(self, kwargs):
        key = kwargs["ui_event"].device().keyString()
        if key in ("h", "j", "k", "l"):
            self.handle_xform(key)
            return(True)
        elif key == "m":
            self.toggle_movement_style()
            self.update_hud()
            return(True)
        elif key in("Shift+-", "Shift+="):
            self.set_zoom_scale(key)
            return(True)
        elif key in("-", "="):
            self.handle_zoom(key)
            return(True)
        else:
            return(False)

    def onMenuAction(self, kwargs):
        action = kwargs["menu_item"]

        # Axes menu

        # Pivot menu
        if action == "pivot_to_origin":
            self.pivot_to_origin()

        # View menu
        elif action == "view_frame":
            self.view_frame()
        elif action == "reset_view":
            self.reset_view()
        elif action == "refit_ui":
            self.refit_ui()
        # elif action == "toggle_grid":
            # self.viewport.settings().setDisplayOrthoGrid(kwargs["toggle_grid"])

        # Zoom menu
        elif action in ("zoom_in", "zoom_out"):
            self.handle_zoom(action)
        elif action in ("zoom_scale_up", "zoom_scale_down"):
            self.set_zoom_scale(action)

        # Xform menu
        elif action in ("xform_left", "xform_up", "xform_down", "xform_right"):
            self.handle_xform(action)

        # Radio section
        elif action == "projection":
            self.set_projection(kwargs["projection"])
        elif action == "movement_style":
            self.movement_style = kwargs["movement_style"]

        # Print section
        elif action == "print_cam_vals":
            self.print_cam_vals()
        elif action == "print_kwargs":
            self.print_kwargs(kwargs)

    def onParmChangeEvent(self, kwargs):
        parm = kwargs["parm_name"]
        # Button
        if parm == "view_frame":
            self.view_frame()
        elif parm == "reset_view":
            self.reset_view()
        # Scale
        elif parm == "axis_scale":
            self.update_axis_drawable()
        # Menu
        elif parm == "projection":
            self.set_projection(kwargs["parm_value"])
        elif parm in ("x_axis", "y_axis", "z_axis"):
            self.update_axis_drawable()

        # Xform
        elif parm == "t":
            if self.state_parms["lock_pivot"]["value"]:
                new_p = kwargs["parm_value"]
                for i in (0, 1, 2):
                    new_p[i] *= -1
                self.state_parms["p"] = new_p
            self.update_cam()
            self.update_pivot_drawable()
            self.update_ray_drawable()
        elif parm == "r":
            self.update_cam()
            self.update_pivot_drawable()
            self.update_ray_drawable()
        elif parm == "p":
            self.update_cam()
            self.update_pivot_drawable()
            self.update_ray_drawable()
        elif parm == "pr":
            self.update_cam()
            self.update_pivot_drawable()
            self.update_ray_drawable()

def make_menu(template):
    menu = hou.ViewerStateMenu("im_view_menu", "IM View Menu")

    # key_context = "h.pane.gview.state.sop.im_view"

    # key_zoom_in         = key_context + ".zoom_in"
    # key_zoom_out        = key_context + ".zoom_out"
    # key_zoom_scale_up   = key_context + ".zoom_scale_up"
    # key_zoom_scale_down = key_context + ".zoom_scale_down"
    # key_xform_left      = key_context + ".xform_left"
    # key_xform_down      = key_context + ".xform_down"
    # key_xform_up        = key_context + ".xform_up"
    # key_xform_right     = key_context + ".xform_right"

    # hou.hotkeys.addContext(key_context,        "im_view operation", "IM view hotkeys")

    # hou.hotkeys.addCommand(key_zoom_in,         "IM Zoom In",         "IM Zoom In")
    # hou.hotkeys.addCommand(key_zoom_out,        "IM Zoom Out",        "IM Zoom Out")
    # hou.hotkeys.addCommand(key_zoom_scale_up,   "IM Zoom Scale Up",   "IM Zoom Scale Up")
    # hou.hotkeys.addCommand(key_zoom_scale_down, "IM Zoom Scale Down", "IM Zoom Scale Down")
    # hou.hotkeys.addCommand(key_xform_left,      "IM xform left",      "IM xform left")
    # hou.hotkeys.addCommand(key_xform_down,      "IM xform down",      "IM xform down")
    # hou.hotkeys.addCommand(key_xform_up,        "IM xform up",        "IM xform up")
    # hou.hotkeys.addCommand(key_xform_right,     "IM xform right",     "IM xform right")

    axis_menu = hou.ViewerStateMenu("axes", "Axes")
    axis_menu.addActionItem("show_all_axes", "Show All Axes")
    axis_menu.addActionItem("disable_all_axes", "Disable All Axes")
    axis_menu.addSeparator()
    axis_menu.addToggleItem("show_x_axis", "X Axis", 1)
    axis_menu.addToggleItem("show_y_axis", "Y Axis", 1)
    axis_menu.addToggleItem("show_z_axis", "Z Axis", 1)
    menu.addMenu(axis_menu)

    pivot_menu = hou.ViewerStateMenu("pivot", "Pivot")
    pivot_menu.addActionItem("pivot_to_origin", "Move to Origin")
    pivot_menu.addToggleItem("lock_pivot", "Lock Pivot", 1)
    menu.addMenu(pivot_menu)

    view_menu = hou.ViewerStateMenu("view", "View")
    view_menu.addActionItem("reset_view",  "Reset")
    view_menu.addActionItem("view_frame",  "Frame All")
    view_menu.addActionItem("refit_ui",    "Refit UI")
    view_menu.addSeparator()
    view_menu.addActionItem("top", "Top")
    view_menu.addActionItem("bottom", "Bottom")
    view_menu.addActionItem("left", "Left")
    view_menu.addActionItem("right", "Right")
    view_menu.addActionItem("front", "Front")
    view_menu.addActionItem("back", "Back")
    menu.addMenu(view_menu)
    # menu.addToggleItem("toggle_grid", "Toggle Grid", 0)

    xform_menu = hou.ViewerStateMenu("xform", "Xform")
    xform_menu.addActionItem("xform_left", "xform left")
    xform_menu.addActionItem("xform_up",  "xform up")
    xform_menu.addActionItem("xform_down", "xform down")
    xform_menu.addActionItem("xform_right", "xform right")
    menu.addMenu(xform_menu)

    zoom_menu = hou.ViewerStateMenu("zoom", "Zoom")
    zoom_menu.addActionItem("zoom_in", "Zoom In")
    zoom_menu.addActionItem("zoom_out", "Zoom Out")
    zoom_menu.addActionItem("zoom_scale_up", "Zoom Scale Up")
    zoom_menu.addActionItem("zoom_scale_down", "Zoom Scale Down")
    menu.addMenu(zoom_menu)

    menu.addSeparator()

    menu.addRadioStrip("projection", "Projection", "orthographic")
    menu.addRadioStripItem("projection", "orthographic", "Orthographic")
    menu.addRadioStripItem("projection", "perspective", "Perspective")

    menu.addRadioStrip("movement_style", "Movement style", "rotate")
    menu.addRadioStripItem("movement_style", "rotate", "Rotate")
    menu.addRadioStripItem("movement_style", "translate", "Translate")

    menu.addSeparator()

    menu.addActionItem("print_cam_vals", "Print Cam Vals")
    menu.addActionItem("print_kwargs", "Print Kwargs")

    template.bindMenu(menu)

def make_parameters(template):
    template.bindParameter(hou.parmTemplateType.Button,
        name="view_frame", label="Frame",
        align=True)
    template.bindParameter(hou.parmTemplateType.Button,
        name="reset_view", label="Reset")

    template.bindParameter(hou.parmTemplateType.Separator, name="sep0",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Int,
        name="axis_scale", label="Axis Scale",
        default_value = 4, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Int,
        name="r_scale", label="Rotation Scale",
        default_value=15, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,
        name="t_scale", label="Translation Scale",
        default_value=1, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,
        name="zoom_scale", label="Zoom Scale",
        default_value=2, toolbox=True)

    template.bindParameter(hou.parmTemplateType.Separator, name="sep1",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Menu,
        name="projection", label="Projection",
        menu_items = (('orthographic', 'Orthographic'), ("perspective", "Perspective")),
        default_value="orthographic", toolbox=False)
    template.bindParameter(hou.parmTemplateType.Menu,
        name="movement_style", label="Movement",
        menu_items = (('rotate', 'Rotate'), ('translate', 'Translate')),
        default_value="rotate", toolbox=False)
    template.bindParameter(hou.parmTemplateType.Toggle,
        name="x_axis", label="X",
        default_value=True, align=True, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Toggle,
        name="y_axis", label="Y",
        default_value=True, align=True, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Toggle,
        name="z_axis", label="Z",
        default_value=True, align=False, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Toggle,
        name="lock_pivot", label="Lock Pivot",
        default_value=1, align=False, toolbox=False)

    template.bindParameter(hou.parmTemplateType.Separator, name="sep2",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Float,
        name="ortho_width", label="Ortho Width",
        default_value=10.0)

    template.bindParameter(hou.parmTemplateType.Separator, name="sep3",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Float,
        name="t", label="Translation",
        num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        name="r", label="Rotation",
        num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        name="p", label="Pivot",
        num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        name="pr", label="Pivot Rotation",
        num_components=3, toolbox=False)

def createViewerStateTemplate():

    # Initialize the state template
    template = hou.ViewerStateTemplate(\
      type_name="im_view",
      label="IM View",
      category=hou.sopNodeTypeCategory(),
      contexts=[hou.objNodeTypeCategory()])

    make_menu(template)
    make_parameters(template)

    # Bind the state handle(s)
    # template.bindHandleStatic("xform", "start_handle",
      # [("startx", "tx"), ("starty", "ty"), ("startz", "tz")])

    # Bind the state icon
    template.bindIcon("DESKTOP_application_sierra")
    # Bind the state
    template.bindFactory(State)


    return template
