MUSCIMA++ 0.9.1
===============

MUSCIMA++ 0.9.1 is a dataset of handwritten music notation symbols.
It contains the positions and classes of over 90 000 notation objects
across 0.9 pages of sheet music. The dataset adds this symbol annotation
as a layer of ground truth over the CVC-MUSCIMA dataset, which already
contains binary images and staff removal ground truth. The symbol annotation
is rich: we annotated both low-level notation primitives and high-level
symbols, and explicitly mark their relationships.

In CVC-MUSCIMA, there is a total of 140 pages: 20 scores transcribed
by 50 musicians each. The article [2] describes how the dataset was
collected. MUSCIMA++ takes 7 versions of each of the 20 scores, taking
care to cover all 50 writers of CVC-MUSCIMA (each writer is represented
no less than twice and no more than three times in the 140 pages
of MUSCIMA++ 0.9.1).

The website of the dataset:

    https://ufal.mff.cuni.cz/muscima




License
-------

(Let's get the legal stuff out of the way.)

The MUSCIMA++ datatset is licensed under the Creative Commons 4.0
Attribution NonCommercial Share-Alike license (CC-BY-NC-SA 4.0).
The full text of the license is in the LICENSE file in this directory.

The attribution requested for MUSCIMA++ is to cite the following
arXiv.org article [1]:

[1]  Jan Hajič jr., Pavel Pecina. In Search of a Dataset for Handwritten 
Optical Music Recognition: Introducing MUSCIMA++. CoRR, arXiv:1703.04824, 
2017. https://arxiv.org/abs/1703.04824

Because MUSCIMA++ is a derivative work of CVC-MUSCIMA, we kindly
request that you follow the attribution rules for CVC-MUSCIMA as well,
and cite article [2]:

[2]  Alicia Fornés, Anjan Dutta, Albert Gordo, Josep Lladós. CVC-MUSCIMA: 
A Ground-truth of Handwritten Music Score Images for Writer Identification 
and Staff Removal. International Journal on Document Analysis and Recognition, 
Volume 15, Issue 3, pp 243-251, 2012. (DOI: 10.0.97/s0.932-010.9168-2).


This basically means you can freely use, distribute, and modify the dataset,
as long as you:

* give credit as requested,
* are not making money off of this (NonCommercial),
* are willing to share derivative work under the same license (ShareAlike).

If you do want to license the dataset under different conditions, 
e.g. if you are a startup looking for training data for your killer 
OMR app, you have to contact us before using the data and we will 
be happy to come up with licensing terms for your specific case.
Anyway, unless you are familiar with the CC-BY-NC-SA license already, 
read the LICENSE file, please!



Ground Truth Definition
-----------------------

We annotated notation primitives (noteheads, stems, beams, barlines), 
as well as higher-level, “semantic” objects (key signatures, voltas, 
measure separators). For each annotated object in an image, we provide 
both the bounding box, and a pixel mask that defines exactly which pixels 
within the bounding box belong to the given object.

In addition to the objects, we annotate their relationships. The relationships
are oriented edges that generally encode attachment: a stem is attached 
to a notehead, a sharp is attached to a key signature, or a barline is attached
to a repeat sign.

We purposefully did not annotate notes, as what constitutes a note on paper 
is not well-defined, and what is traditionally considered a “note” graphical 
object does not map well onto the musical concept of a “note” with a pitch, 
duration, amplitude, and timbre. Instead of defining graphical note objects, 
we define relationships between notation primitives, so that the musical notes 
can be deterministically reconstructed. Notehead primitives (notehead-full, 
notehead-empty, and their grace note counterparts) should provide a 1:1 interface 
to major notation semantics representations such as MusicXML or MEI.

Formally, the annotation is a directed graph of notation objects, each of which 
is associated with a subset of foreground pixels in the annotated image. We do 
our best to keep this graph acyclic.

The full definition the MUSCIMA++ ground truth (current version 0.9) is captured 
in the annotation guidelines:

    http://muscimarker.readthedocs.io/en/develop/instructions.html


To get the images that were annotated, you will first need to download 
the CVC-MUSCIMA staff removal dataset:

    http://www.cvc.uab.es/cvcmuscima/index_database.html

You can then use the get_images_from_muscima.py script from the muscima package 
(see below), with input from specifications/cvc-muscima-image-list.txt, and 
specify data/images as the target directory. This will extract the 140 annotated
symbol images for which there are annotations, with the correct filenames.





Tools
-----

Apart from the symbol annotation data themselves, we also provide 
two Python pacakges:

* muscima (https://github.com/hajicj/muscima): 
  implements I/O for MUSCIMA++ annotations and the data model
  (pip install muscima)
* MUSCIMarker (https://github.com/hajicj/MUSCIMarker):
  the annotation and visualization tool used to create the dataset.
  (For installation, see: https://muscimarker.readthedocs.io/en/latest/)


We believe the functionality in muscima will make it easier for you 
to use the dataset. You don’t need MUSCIMarker unless you want to extend 
the dataset, although it is also nifty for looking at the data.

If you do not want to use the Python interface, you can of course make your 
own. The data is stored as a regular XML file, described in detail below 
(and also in the muscima.io module).





Dataset directory structure
---------------------------

The dataset package has the following structure:

+--+ MUSCIMA-pp_v1.0/
   |
   +--+ data/                               ... Contains the data files.
   |  +--+ cropobjects_manual/              ... Contains the annotation files without automatically
   |  |                                         extracted staff objects and their relationships.
   |  +--+ cropobjects_withstaff/           ... Contains the annotation files enriched by staff objects,
   |  |                                         inferred automatically from CVC-MUSCIMA staff-only images
   |  |                                         using scripts from the ``muscima’’ package.
   |  |  +--- CVC-MUSCIMA_W-01_N-10_D-ideal.xml
   |  |  +...
   |  |
   |  +--+ images/                          ... Put corresponding CVC-MUSCIMA image files here.
   |                                            (Analogously, use e.g. data/fulls/ for full images.)
   |
   +--+ specifications/                             ... Contains the ground truth definition files for MUSCIMarker:
   |  +--- cvc-muscima-image-list.txt               ... list of CVC-MUSCIMA images used for annotation,
   |  +--- mff-muscima-mlclasses-annot.xml          ... list of object classes,
   |  +--- mff-muscima-mlclasses-annot.deprules     ... and list of rules governing their relationships.
   |  +-—- testset-dependent.txt                    ... List of writer-dependent test set images. 
   |  |                                                 (Same handwriting in training and test set.)
   |  +-—- testset-independent.txt                  ... List of writer-dependent test set images.
   |                                                    (Test set handwriting never seen in training set.)
   | 
   +--- LICENSE                             ... The legal stuff (CC-BY-NC-SA 4.0, which is fine 
   |                                            unless you want to make money off of this data).
   +--- ERRATA                              ... File which lists errors in the data and their corrections. 
   +--- README                              ... This file.

I




Data Formats
------------

The MUSCIMA++ annotations are provided as XML files.
The data itself is inside <CropObject> elements:

    <CropObject xml:id="MUSCIMA-pp_0.9___CVC-MUSCIMA_W-35_N-08_D-ideal___25">
      <Id>25</Id>
      <MLClassName>grace-notehead-full</MLClassName>
      <Top>119</Top>
      <Left>413</Left>
      <Width>16</Width>
      <Height>6</Height>
      <Mask>1:5 0:11 (...) 1:4 0:6 1:5 0:1</Mask>
      <Outlinks>12 24 26</Outlinks>
      <Inlinks>13</Inlinks>
    </CropObject>

The CropObjects are themselves kept as a list, which is the top-level
element in the data files:

    <CropObjectList>
      <CropObjects>
        <CropObject xml:id="..."> ... </CropObject>
        <CropObject xml:id="..."> ... </CropObject>
      </CropObjects>
    </CropObjectList>


********************************************************************************
*                                                                              *
*   NOTE                                                                       *
*                                                                              *
*   Parsing (muscima.io.parse_cropobject_list()) is only implemented for       *
*   files that consist of a single <CropObjectList>.                           *
*                                                                              *
********************************************************************************


The value of the xml:id attribute of the <CropObject> element
is a string that uniquely identifies the CropObject
in the entire dataset. It is derived from a global dataset name and version
identifier (the + signs in MUSCIMA++ 1.0 unfortunately do not comply
with the XML specification for the xml:id value), a CropObjectList identifier
which is unique within the dataset (derived from the filename:
usually in the format CVC-MUSCIMA_W-{:02}_N-{:02}_D-ideal),
and the number of the CropObject within the given CropObjectList
(which matches the <Id> value). The delimiter is three underscores
(___), in order to comply with XML rules for the xml:id attribute.



Individual elements of a <CropObject>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* <Id> is the integer ID of the CropObject inside a given
  <CropObjectList> (which generally corresponds to one XML file
  of CropObjects -- see below for unique ID policy and dataset namespaces).
* <MLClassName> is the name of the object's class (such as
  notehead-full, beam, numeral_3, etc.).
* <Top> is the vertical coordinate of the upper left corner of the object's
  bounding box.
* <Left> is the horizontal coordinate of the upper left corner of
  the object's bounding box.
* <Width>: the amount of rows that the CropObject spans.
* <Height>: the amount of columns that the CropObject spans.
* <Mask>: a run-length-encoded binary (0/1) array that denotes the area
  within the CropObject's bounding box (specified by top, left,
  height and width) that the CropObject actually occupies. If
  the mask is not given, the object is understood to occupy the entire
  bounding box (within MUSCIMA++ 1.0, all objects have explicit masks,
  but the format enables annotating bounding boxes only). The run-length
  encoding is obtained from a flattened version of the binary array
  in the C order, using the flatten() method of numpy
  arrays. (The mask lines might get quite long, but e.g. the lxml library
  has no problems with parsing them.)
* <Inlinks>: whitespace-separated objid list, representing CropObjects
  **from** which a relationship leads to this CropObject. (Relationships are
  directed edges, forming a directed graph of CropObjects.) The objids are
  valid in the same scope as the CropObject's objid: don't mix
  CropObjects from multiple scopes (e.g., multiple CropObjectLists)!
  If you are using CropObjects from multiple CropObjectLists at the same
  time, make sure to check against the uid.
* <Outlinks>: whitespace-separate objid list, representing CropObjects
  **to** which a relationship leads to this CropObject. (Relationships are
  directed edges, forming a directed graph of CropObjects.) The objids are
  valid in the same scope as the CropObject's objid: don't mix
  CropObjects from multiple scopes (e.g., multiple CropObjectLists)!
  If you are using CropObjects from multiple CropObjectLists at the same
  time, make sure to check against the uid.

The parser function provided for CropObjects does *not* check against
the presence of other sub-elements. You can therefore extend CropObjects
for your own purposes.


********************************************************************************
*                                                                              *
*   NOTE                                                                       *
*                                                                              *
*   The full description of the format is also given in the muscima            *
*   package, module musicma.cropobject. In case these two versions             *
*   do not match, the authoritative document is the package documentation.     *
*                                                                              *
********************************************************************************



Unique IDs policy
^^^^^^^^^^^^^^^^^

Each CropObject has two identifiers: one is a dataset-wide
unique identifier, and one is an integer ID that is valid
within the scope of annotation of one document.

The xml:id serves to identify the CropObject uniquely,
at least within the MUSCIMA dataset system. (We anticipate further
versions of the dataset, and need to plan for that.)

To uniquely identify a CropObject, we need three "levels":

* The "global", **dataset-level identification**: which dataset is this
  CropObject coming from? (For this dataset: MUSCIMA-pp_1.0.
  Unfortunately, rules for XML NAME-type attributes do not allow
  the + character in the attribute value.)
* The "local", **document-level identification**: which document
  (within the given dataset) is this CropObject coming from?
  For MUSCIMA++ 1.0, this will usually be a string like
  CVC-MUSCIMA_W-35_N-08_D-ideal, derived from the filename
  under which the CropObjectList containing the given CropObject
  is stored.
* The **within-document identification**, which is an integer
  identical to the <Id>.

These three components are joined together into one string by
a delimiter: ___

The full xml:id of a CropObject then might look like this:

  MUSCIMA-pp_0.9__CVC-MUSCIMA_W-35_N-08_D-ideal___611

You will need to use UIDs whenever you are combining CropObjects
from different documents, and/or datasets. (If you are really combining
datasets, make sure you know what you are doing -- some annotation
instructions may change between versions, so objects of the same class
might not exactly correspond to each other...)

On the other hand, the <Id> field is intended to uniquely identify
a CropObject *within the scope of one CropObject list* (one annotation
document), and enable integer manipulation. (We admit this is a bit
of a legacy issue, connected to the annotation tool, which assumes
that there is an integer identification of CropObjects when annotating
a single document.)


********************************************************************************
*                                                                              *
*   CAUTION                                                                    *
*                                                                              *
*   The scope of unique identification within MUSCIMA++ is only within         *
*   a <CropObjectList>. Don't use objid to mix CropObjects from                *
*   multiple files! Use their uid attribute, which is taken from               *
*   the <CropObject> element's xml:id.                                         *
*                                                                              *
********************************************************************************



CropObjectClass
^^^^^^^^^^^^^^^

The list of symbol classes used for MUSCIMA++ 0.9 is provided in
the specifications/mff-muscima-classes-annot.xml file. See the
muscima.io module documentation for details on the CropObject classes file
format. (You do not have to worry about this unless you want to perform symbol
relationship validation.)



Relationships grammar
^^^^^^^^^^^^^^^^^^^^^

The allowed relationships are listed in the file
specifications/mff-mucsima-classes-annot.deprules. See the
muscima.grammar module documentation for the *.deprules file format
details. (You do not have to worry about this unless you want to perform
symbol relationship validation.)



Designated test sets
--------------------

In order to promote replicable comparison across experiments, we provide
two suggested train/test splits: a "writer-independent" split, where
the test set is selected so that no image by a test set writer appears
in the training data (so that you test on unseen handwriting), and
a "writer-dependent" split, which is the opposite: every writer in
the test set also has (another) image in the training set.

Both of the test sets contain one instance of each page (so there are
20 test pages in each).

To get the indexes for a test set (in this case, writer-independnet):

  paste <(seq 140) <(ls data/cropobjects/) 
    | grep -f specifications/testset-independent.txt
    | cut -f 1



Known issues
------------

The MUSCIMA++ dataset is not perfect, as is always the case with extensive
human-annotated datasets. In the interest of full disclosure and managing
expectations, we list the known issues. We will do our best to deal with them
in follow-up version of MUSCIMA++. If you find some errors that are not on this
list and should be, especially problems that seem systematic, feel free to drop
us a line at::

    hajicj@ufal.mff.cuni.cz

Of course, we will greatly appreciate any effort towards fixing these issues!

We hope that this dataset is going to eventually become an OMR community effort,
with all the bells and whistles -- including co-authorship credit for future
versions, esp. if you come up with bug-hunting and/or annotation automation.



Staff removal artifacts
^^^^^^^^^^^^^^^^^^^^^^^

The CVC-MUSCIMA dataset has had staff lines removed automatically with very high
accuracy, based on a precise writing and scanning setup (using a standard notation
paper and a specific pen across all 50 writers). However, there are still some
errors in staff removal: sometimes, the staff removal algorithm took with it
some pixels that were also legitimate part of a symbol. This manifests itself
most frequently with stems.



Human Errors
^^^^^^^^^^^^

Annotators also might have made mistakes that slipped both through automated
validation and manual quality control. In automated validation, there is
a tradeoff between catching errors and false alarms: music notation is
*complicated*, and things like multiple stems per notehead happen even
in the limited set of 20 pages of MUSCIMA++. In the same vein, although we did
implement automated checks for bad inaccuracies, they only catch some
of the problems as well, and our manual quality control procedure also relies
on inherently imperfect human judgment.

Moral of the story: if your models are doing weird things, cross-validate,
isolate the problematic data points, and drop us a line. We will try
to maintain a list of "known offender" CropObjects this way, so that
other users will be able to benefit from your discoveries as well,
and keep releasing corrected versions.



UPDATE (0.9.1) 
^^^^^^^^^^^^^^

2017-08-17: Huge thanks to Alexander Pacha 
(https://www.ims.tuwien.ac.at/people/alexander-pacha) 
for a thorough look at all the symbols and providing the ERRATA file.
I’ve fixed the errors he found. [JH]



Contact
-------

If you wish to contact the authors of this dataset, write to:

  hajicj@ufal.mff.cuni.cz

We will be happy to hear your feedback!

