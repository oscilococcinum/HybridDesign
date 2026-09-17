# HybridDesign Workbench

Custom FreeCAD Workbench for advanced modeling and OCCT-powered geometry creation. It was inspired by the capabilities of the CATIA V5 GSD Workbench.
Since CATIA has a well-known and established surfacing workflow, it might (or might not) be a good idea, to bring some of those features into FreeCAD.

<img src="/Assets/HybridDesignWorkbench.svg" width="128"/>

## Overview

This workbench extends FreeCAD with the following features:

- AutoFillet
- Boundary
- CutSolid
- Defeature (Parametric)
- Surface Extrusion
- Extract

---

## Features

### AutoFillet

<img src="/Assets/AutoFillet_HybridDesign.svg" width="64"/>

![autofillet gif](docs/gifs/autofillet.gif)

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

<img src="/Assets/Defeature_HybridDesign.svg" width="64"/>

![defeature gif](docs/gifs/defeature.gif)

Implements the Part Defeature command within the PartDesign workflow (inside a Body) and makes it parametric.

#### Benefits

- Integrated into PDBody
- Full parametric control

---

### Extrusion

<img src="/Assets/Extrusion_HybridDesign.svg" width="64"/>

![extrusion gif](docs/gifs/extrusion.gif)

An implementation of `Part::Extrude`. Still a work in progress.

#### Supported Inputs

- Sketches
- Wires
- Edges

---

### Extract

<img src="/Assets/Extract_HybridDesign.svg" width="64"/>

![extract gif](docs/gifs/extract.gif)

Implements surface extraction (single-face or multi-face) with filtering options.

The tangency filter is probably the most promising feature.

#### Supported Inputs

- Faces/Surfaces
- Tree View surface/face containers

---

### CutSolid

<img src="/Assets/CutSolid_HybridDesign.svg" width="64"/>

![cutsolid gif](docs/gifs/cutsolid.gif)

Implements cutting a PDBody using surface objects.

#### Supported Inputs

- Faces/Surfaces

---

### OffsetSurface

<img src="/Assets/OffsetSurface_HybridDesign.svg" width="64"/>

![suroffset gif](docs/gifs/offsetsurface.gif)

Implementation of the Part Offset tool.

#### Supported Inputs

- Faces/Surfaces

---

### Boundary

<img src="/Assets/Boundary_HybridDesign.svg" width="64"/>

![boundary gif](docs/gifs/boundary.gif)

Extracts outer wires, inner wires, or any boundary wire in between.

#### Supported Inputs

- Faces/Surfaces

---

### TangentSelection

<img src="/Assets/TangentSelection_HybridDesign.svg" width="64"/>

![tangentselection gif](docs/gifs/tangentselection.gif)

Propagates selection onto faces tangent to the seed face, until sharp corrner.

#### Supported Inputs

- Faces/Surfaces

---

### EnclosedSelection

<img src="/Assets/EnclosedSelection_HybridDesign.svg" width="64"/>

![enclosedselection gif](docs/gifs/enclosedselection.gif)

Propagates selection onto faces based on seed face until it encounters boundary faces.

#### Supported Inputs

- Faces/Surfaces

---

### ThickenSurface

<img src="/Assets/ThickenSurface_HybridDesign.svg" width="64"/>

![ThickenSurface gif](docs/gifs/thickensurface.gif)

Creates solid by offseting surface.

#### Supported Inputs

- Faces/Surfaces

---

### SplitSurface

<img src="/Assets/SplitSurface_HybridDesign.svg" width="64"/>

![splitsurface gif](docs/gifs/splitsurface.gif)

Cuts first selected surface with second as cutting tool.

#### Supported Inputs

- Faces/Surfaces
---

### ShapeFillet

<img src="/Assets/ShapeFillet_HybridDesign.svg" width="64"/>

![ShapeFillet gif](docs/gifs/shapefillet.gif)

Creates fillet betwen surfaces based on intersection.
WIP! Surfaces have to idealy intersect !

#### Supported Inputs

- Faces/Surfaces

### CurvedHelix

<img src="/Assets/CurvedHelix_HybridDesign.svg" width="64"/>

![curvedhelix gif](docs/gifs/curvedhelix.gif)

Creates curved helix along the spine.

#### Supported Inputs

- Wires/Sketches
