# HybridDesign Workbench

Custom FreeCAD Workbench for advanced modeling and OCCT-powered geometry creation. It was inspired by the capabilities of the CATIA V5 GSD Workbench.
Since CATIA has a well-known and established surfacing workflow, it might (or might not) be a good idea, to bring some of those features into FreeCAD.
WB is in Alpha stage.

<img src="Resources/Icons/HybridDesignWorkbench.svg" width="128"/>

## Features

### AutoFillet

<img src="Resources/Icons/AutoFillet_HybridDesign.svg" width="64"/>

![autofillet gif](Resources/Media/autofillet.gif)

Enables users to create fillets based on the previous feature in a PDBody.
The edges to be filleted are selected according to the `FilterType` property.

Support for non-straight edges (e.g. arcs, B-splines) is still a work in progress.

#### Example Workflow

1. Add a snap-fit clip using a boolean operation.
2. Launch the command.
3. Choose the `Intersection` FilterType.
4. The edges at the intersection of the new snap-fit feature and the base feature are filleted.

---

### Defeature (Parametric)

<img src="Resources/Icons/Defeature_HybridDesign.svg" width="64"/>

![defeature gif](Resources/Media/defeature.gif)

Implements the Part Defeature command within the PartDesign workflow (inside a Body) and makes it parametric.

#### Benefits

- Integrated into PDBody
- Full parametric control

---

### Extrusion

<img src="Resources/Icons/Extrusion_HybridDesign.svg" width="64"/>

![extrusion gif](Resources/Media/extrusion.gif)

An implementation of `Part::Extrude`. Still a work in progress.

#### Supported Inputs

- Sketches
- Wires
- Edges

---

### Extract

<img src="Resources/Icons/Extract_HybridDesign.svg" width="64"/>

![extract gif](Resources/Media/extract.gif)

Implements surface extraction (single-face or multi-face) with filtering options.

The tangency filter is probably the most promising feature.

#### Supported Inputs

- Faces/Surfaces
- Tree View surface/face containers

---

### CutSolid

<img src="Resources/Icons/CutSolid_HybridDesign.svg" width="64"/>

![cutsolid gif](Resources/Media/cutsolid.gif)

Implements cutting a PDBody using surface objects.

#### Supported Inputs

- Faces/Surfaces

---

### OffsetSurface

<img src="Resources/Icons/OffsetSurface_HybridDesign.svg" width="64"/>

![suroffset gif](Resources/Media/offsetsurface.gif)

Implementation of the Part Offset tool.

#### Supported Inputs

- Faces/Surfaces

---

### Boundary

<img src="Resources/Icons/Boundary_HybridDesign.svg" width="64"/>

![boundary gif](Resources/Media/boundary.gif)

Extracts outer wires, inner wires, or any boundary wire in between.

#### Supported Inputs

- Faces/Surfaces

---

### TangentSelection

<img src="Resources/Icons/TangentSelection_HybridDesign.svg" width="64"/>

![tangentselection gif](Resources/Media/tangentselection.gif)

Propagates selection onto faces tangent to the seed face, until sharp corrner.

#### Supported Inputs

- Faces/Surfaces

---

### EnclosedSelection

<img src="Resources/Icons/EnclosedSelection_HybridDesign.svg" width="64"/>

![enclosedselection gif](Resources/Media/enclosedselection.gif)

Propagates selection onto faces based on seed face until it encounters boundary faces.

#### Supported Inputs

- Faces/Surfaces

---

### ThickenSurface

<img src="Resources/Icons/ThickenSurface_HybridDesign.svg" width="64"/>

![ThickenSurface gif](Resources/Media/thickensurface.gif)

Creates solid by offseting surface.

#### Supported Inputs

- Faces/Surfaces

---

### SplitSurface

<img src="Resources/Icons/SplitSurface_HybridDesign.svg" width="64"/>

![splitsurface gif](Resources/Media/splitsurface.gif)

Cuts first selected surface with second as cutting tool.

#### Supported Inputs

- Faces/Surfaces

---

### ShapeFillet

<img src="Resources/Icons/ShapeFillet_HybridDesign.svg" width="64"/>

![ShapeFillet gif](Resources/Media/shapefillet.gif)

Creates fillet betwen surfaces based on intersection.
WIP! Surfaces have to idealy intersect !

#### Supported Inputs

- Faces/Surfaces

---

### Extrapolate

<img src="Resources/Icons/Extrapolate_HybridDesign.svg" width="64"/>

![Extrapolate gif](Resources/Media/extrapolate.gif)

Extrapolates shell based on selectet boundary (list of edges).
WIP! Gaps betwen extrapolated surfaces are not filled.

#### Supported Inputs

- Edges

### CurvedHelix

<img src="Resources/Icons/CurvedHelix_HybridDesign.svg" width="64"/>

![curvedhelix gif](Resources/Media/curvedhelix.gif)

Creates curved helix along the spine.

#### Supported Inputs

- Wires/Sketches
