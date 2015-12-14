import logging, qt, ctk, os, slicer


class ModuleWidgetMixin(object):

  @property
  def layoutManager(self):
    return slicer.app.layoutManager()

  @property
  def dicomDatabase(self):
    return slicer.dicomDatabase

  @staticmethod
  def makeProgressIndicator(maxVal, initialValue=0):
    progressIndicator = qt.QProgressDialog()
    progressIndicator.minimumDuration = 0
    progressIndicator.modal = True
    progressIndicator.setMaximum(maxVal)
    progressIndicator.setValue(initialValue)
    progressIndicator.setWindowTitle("Processing...")
    progressIndicator.show()
    progressIndicator.autoClose = False
    return progressIndicator

  @staticmethod
  def confirmDialog(message, title='SliceTracker'):
    result = qt.QMessageBox.question(slicer.util.mainWindow(), title, message,
                                     qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
    return result == qt.QMessageBox.Ok

  @staticmethod
  def notificationDialog(message, title='SliceTracker'):
    return qt.QMessageBox.information(slicer.util.mainWindow(), title, message)

  @staticmethod
  def yesNoDialog(message, title='SliceTracker'):
    result = qt.QMessageBox.question(slicer.util.mainWindow(), title, message,
                                     qt.QMessageBox.Yes | qt.QMessageBox.No)
    return result == qt.QMessageBox.Yes

  @staticmethod
  def warningDialog(message, title='SliceTracker'):
    return qt.QMessageBox.warning(slicer.util.mainWindow(), title, message)

  def getSetting(self, setting):
    settings = qt.QSettings()
    return str(settings.value(self.moduleName + '/' + setting))

  def setSetting(self, setting, value):
    settings = qt.QSettings()
    settings.setValue(self.moduleName + '/' + setting, value)

  def createHLayout(self, elements, parent=None, **kwargs):
    return self._createLayout(qt.QHBoxLayout, elements, parent, **kwargs)

  def createVLayout(self, elements, parent=None, **kwargs):
    return self._createLayout(qt.QVBoxLayout, elements, parent, **kwargs)

  def _createLayout(self, layoutClass, elements, parent, **kwargs):
    widget = qt.QWidget(parent)
    rowLayout = layoutClass(parent)
    widget.setLayout(rowLayout)
    for element in elements:
      rowLayout.addWidget(element)
    for key, value in kwargs.iteritems():
      if hasattr(rowLayout, key):
        setattr(rowLayout, key, value)
    return widget

  def createIcon(self, filename, iconPath=None):
    if not iconPath:
      iconPath = os.path.join(self.modulePath, 'Resources/Icons')
    path = os.path.join(iconPath, filename)
    pixmap = qt.QPixmap(path)
    return qt.QIcon(pixmap)

  def createLabel(self, title, **kwargs):
    label = qt.QLabel(title)
    return self.extendQtGuiElementProperties(label, **kwargs)

  def createButton(self, title, **kwargs):
    button = qt.QPushButton(title)
    button.setCursor(qt.Qt.PointingHandCursor)
    return self.extendQtGuiElementProperties(button, **kwargs)

  def createDirectoryButton(self, **kwargs):
    button = ctk.ctkDirectoryButton()
    for key, value in kwargs.iteritems():
      if hasattr(button, key):
        setattr(button, key, value)
    return button

  def extendQtGuiElementProperties(self, element, **kwargs):
    for key, value in kwargs.iteritems():
      if hasattr(element, key):
        setattr(element, key, value)
      else:
        if key == "fixedHeight":
          element.minimumHeight = value
          element.maximumHeight = value
        elif key == 'hidden':
          if value:
            element.hide()
          else:
            element.show()
        else:
          logging.error("%s does not have attribute %s" % (element.className(), key))
    return element

  def createComboBox(self, **kwargs):
    combobox = slicer.qMRMLNodeComboBox()
    combobox.addEnabled = False
    combobox.removeEnabled = False
    combobox.noneEnabled = True
    combobox.showHidden = False
    for key, value in kwargs.iteritems():
      if hasattr(combobox, key):
        setattr(combobox, key, value)
      else:
        logging.error("qMRMLNodeComboBox does not have attribute %s" % key)
    combobox.setMRMLScene(slicer.mrmlScene)
    return combobox


class ModuleLogicMixin(object):

  @staticmethod
  def createDirectory(directory, message=None):
    if message:
      logging.debug(message)
    try:
      os.makedirs(directory)
    except OSError:
      logging.debug('Failed to create the following directory: ' + directory)

  @staticmethod
  def getDICOMValue(currentFile, tag, fallback=None):
    db = slicer.dicomDatabase
    try:
      value = db.fileValue(currentFile, tag)
    except RuntimeError:
      logging.info("There are problems with accessing DICOM values from file %s" % currentFile)
      value = fallback
    return value

  @staticmethod
  def getFileList(directory):
    return [f for f in os.listdir(directory) if ".DS_Store" not in f]

  @staticmethod
  def importStudy(dicomDataDir):
    indexer = ctk.ctkDICOMIndexer()
    indexer.addDirectory(slicer.dicomDatabase, dicomDataDir)
    indexer.waitForImportFinished()

  @staticmethod
  def createScalarVolumeNode(name):
    volume = slicer.vtkMRMLScalarVolumeNode()
    volume.SetName(name)
    slicer.mrmlScene.AddNode(volume)
    return volume

  @staticmethod
  def createTransformNode(name, isBSpline):
    node = slicer.vtkMRMLBSplineTransformNode() if isBSpline else slicer.vtkMRMLLinearTransformNode()
    node.SetName(name)
    slicer.mrmlScene.AddNode(node)
    return node