import os
import unittest
import csv
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

#
# NeedleGuideTemplate
#

class NeedleGuideTemplate(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "NeedleGuideTemplate" # TODO make this more human readable by adding spaces
    self.parent.categories = ["IGT"]
    self.parent.dependencies = []
    self.parent.contributors = ["Junichi Tokuda (Brigham and Women's Hospital)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    The NeedleGuideTemlpate module guides image-guided percutaneous interventions with needle-guide template.
    The module calculates identify the needle guide hole and needle insertion depth to reach to the target
    specified on the image. 
    """
    self.parent.acknowledgementText = """
    This module is developed by Junichi Tokuda with support from NIH grants P41EB015898 (PI: Jolesz, Tempany) and R01CA111288 (PI: Tempany)
    based on ScriptedLoadableModule template developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.
    and was partially funded by NIH grant 3P41RR013218-12S1.
    """

#
# NeedleGuideTemplateWidget
#

class NeedleGuideTemplateWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    # Instantiate and connect widgets ...

    self.logic = NeedleGuideTemplateLogic(None)

    #--------------------------------------------------
    # For debugging
    #
    # Reload and Test area
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    reloadCollapsibleButton.collapsed = True
    
    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "NeedleGuideTemlpate Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)
    #
    #--------------------------------------------------

    #--------------------------------------------------
    #
    # Configuration
    #
    configCollapsibleButton = ctk.ctkCollapsibleButton()
    configCollapsibleButton.text = "Configuration"
    self.layout.addWidget(configCollapsibleButton)

    configFormLayout = qt.QFormLayout(configCollapsibleButton)

    configCollapsibleButton.collapsed = True

    templateConfigPathLayout = qt.QHBoxLayout()
    
    self.templateConfigPathEdit = qt.QLineEdit()
    self.templateConfigPathEdit.text = ""
    self.templateConfigPathEdit.readOnly = False
    self.templateConfigPathEdit.frame = True
    self.templateConfigPathEdit.styleSheet = "QLineEdit { background:transparent; }"
    self.templateConfigPathEdit.cursor = qt.QCursor(qt.Qt.IBeamCursor)
    templateConfigPathLayout.addWidget(self.templateConfigPathEdit)

    self.templateConfigButton = qt.QPushButton("...")
    self.templateConfigButton.toolTip = "Choose a template configuration file"
    self.templateConfigButton.enabled = True
    self.templateConfigButton.connect('clicked(bool)', self.onTemplateConfigButton)
    templateConfigPathLayout.addWidget(self.templateConfigButton)

    configFormLayout.addRow("Template Config File: ", templateConfigPathLayout)

    fiducialConfigPathLayout = qt.QHBoxLayout()
    
    self.fiducialConfigPathEdit = qt.QLineEdit()
    self.fiducialConfigPathEdit.text = ""
    self.fiducialConfigPathEdit.readOnly = False
    self.fiducialConfigPathEdit.frame = True
    self.fiducialConfigPathEdit.styleSheet = "QLineEdit { background:transparent; }"
    self.fiducialConfigPathEdit.cursor = qt.QCursor(qt.Qt.IBeamCursor)
    fiducialConfigPathLayout.addWidget(self.fiducialConfigPathEdit)

    self.fiducialConfigButton = qt.QPushButton("...")
    self.fiducialConfigButton.toolTip = "Choose a fiducial configuration file"
    self.fiducialConfigButton.enabled = True
    self.fiducialConfigButton.connect('clicked(bool)', self.onFiducialConfigButton)
    fiducialConfigPathLayout.addWidget(self.fiducialConfigButton)

    configFormLayout.addRow("Fiducial Config File: ", fiducialConfigPathLayout)


    #
    # Main Area
    #
    mainCollapsibleButton = ctk.ctkCollapsibleButton()
    mainCollapsibleButton.text = "Main"
    self.layout.addWidget(mainCollapsibleButton)

    # Layout within the dummy collapsible button
    mainFormLayout = qt.QFormLayout(mainCollapsibleButton)

    self.showTemplateCheckBox = qt.QCheckBox()
    self.showTemplateCheckBox.checked = 0
    self.showTemplateCheckBox.setToolTip("Show 3D model of the template")
    mainFormLayout.addRow("Show Template:", self.showTemplateCheckBox)
    self.showTemplateCheckBox.connect('toggled(bool)', self.onShowTemplate)

    self.showFiducialCheckBox = qt.QCheckBox()
    self.showFiducialCheckBox.checked = 0
    self.showFiducialCheckBox.setToolTip("Show 3D model of the fiducial")
    mainFormLayout.addRow("Show Fiducial:", self.showFiducialCheckBox)
    self.showFiducialCheckBox.connect('toggled(bool)', self.onShowFiducial)

    self.showTrajectoriesCheckBox = qt.QCheckBox()
    self.showTrajectoriesCheckBox.checked = 0
    self.showTrajectoriesCheckBox.setToolTip("Show 3D model of the fiducial")
    mainFormLayout.addRow("Show Trajectories:", self.showTrajectoriesCheckBox)
    self.showTrajectoriesCheckBox.connect('toggled(bool)', self.onShowTrajectories)

    
    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    mainFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.outputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.outputSelector.selectNodeUponCreation = False
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    mainFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    mainFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # scale factor for screen shots
    #
    self.screenshotScaleFactorSliderWidget = ctk.ctkSliderWidget()
    self.screenshotScaleFactorSliderWidget.singleStep = 1.0
    self.screenshotScaleFactorSliderWidget.minimum = 1.0
    self.screenshotScaleFactorSliderWidget.maximum = 50.0
    self.screenshotScaleFactorSliderWidget.value = 1.0
    self.screenshotScaleFactorSliderWidget.setToolTip("Set scale factor for the screen shots.")
    mainFormLayout.addRow("Screenshot scale factor", self.screenshotScaleFactorSliderWidget)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    mainFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = NeedleGuideTemplateLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    screenshotScaleFactor = int(self.screenshotScaleFactorSliderWidget.value)
    print("Run the algorithm")
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), enableScreenshotsFlag,screenshotScaleFactor)

  def onReload(self, moduleName="NeedleGuideTemplate"):
    # Generic reload method for any scripted module.
    # ModuleWizard will subsitute correct default moduleName.

    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onTemplateConfigButton(self):
    path = self.templateConfigPathEdit.text
    path = qt.QFileDialog.getOpenFileName(None, 'Open Template File', path, '*.csv')
    self.templateConfigPathEdit.setText(path)
    self.logic.loadTemplateConfigFile(path)
    

  def onFiducialConfigButton(self):
    path = self.fiducialConfigPathEdit.text
    filename = qt.QFileDialog.getOpenFileName(None, 'Open Fiducial File', path, '.csv')
    self.fiducialConfigPathEdit.setText(path)

  def onShowTemplate(self):
    pass

  def onShowFiducial(self):
    pass

  def onShowTrajectories(self):
    pass


#
# NeedleGuideTemplateLogic
#

class NeedleGuideTemplateLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModuleLogic.__init__(self, parent)

    self.fiducialName = ''
    self.fiducialConfig = []
    self.templateName = ''
    self.templateConfig = []
    self.templateModelNodeID = ''

  def loadFiducialConfigFile(self, path):
    reader = csv.reader(open(path, 'rb'))
        
  def loadTemplateConfigFile(self, path):
    header = False
    reader = csv.reader(open(path, 'rb'))
    try:
      for row in reader:
        if header:
          self.templateConfig.append(row)
          print row
        else:
          self.templateName = row[0]
          header = True
    except csv.Error as e:
      print('file %s, line %d: %s' % (filename, reader.line_num, e))

    self.createTemplateModel()

  def createTemplateModel(self):
    
    mnode = slicer.mrmlScene.GetNodeByID(self.templateModelNodeID)
    if mnode == None:
      mnode = slicer.vtkMRMLModelNode()
      mnode.SetName('NeedleGuideTemplate')
      slicer.mrmlScene.AddNode(mnode)
      self.templateModelNodeID = mnode.GetID()

      modelDisplayNode = slicer.vtkMRMLModelDisplayNode()
      #modelDisplayNode.SetColor(self.ModelColor)
      slicer.mrmlScene.AddNode(modelDisplayNode)
      mnode.SetAndObserveDisplayNodeID(modelDisplayNode.GetID())
      
    append = vtk.vtkAppendPolyData()
    
    for row in self.templateConfig:
      cylinderSource = vtk.vtkCylinderSource()
      cx = (float(row[2])+float(row[5]))/2.0
      cy = (float(row[3])+float(row[6]))/2.0
      cz = (float(row[4])+float(row[7]))/2.0
      cylinderSource.SetCenter(cx, cy, cz)
      cylinderSource.SetRadius(5.0)
      cylinderSource.SetHeight(7.0)
      cylinderSource.SetResolution(100)
      cylinderSource.Update()

      if vtk.VTK_MAJOR_VERSION <= 5:
        append.AddInput(cylinderSource.GetOutput());
      else:
        append.AddInputData(cylinderSource.GetOutput());

      append.Update()
      mnode.SetAndObservePolyData(append.GetOutput())
 

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    self.delayDisplay(description)

    if self.enableScreenshots == 0:
      return

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, self.screenshotScaleFactor, imageData)

  def run(self,inputVolume,outputVolume,enableScreenshots=0,screenshotScaleFactor=1):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

    self.enableScreenshots = enableScreenshots
    self.screenshotScaleFactor = screenshotScaleFactor

    self.takeScreenshot('NeedleGuideTemplate-Start','Start',-1)

    return True


class NeedleGuideTemplateTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_NeedleGuideTemplate1()

  def test_NeedleGuideTemplate1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = NeedleGuideTemplateLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
