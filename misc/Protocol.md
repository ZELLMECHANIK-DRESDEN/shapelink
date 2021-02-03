# Shape-Link (Shape-In plug-in interface)

Provide a Shape-Link-in interface for user-created Shape-In extensions

# Protocol Draft

```plantuml
Shape-In -> Shape-Link : Register Datafields
activate Shape-Link
Shape-Link -> Shape-In : ACK
|||
|||
    loop while measurement is running
        Shape-In -> Shape-Link : Data package (QDataStream)
        Shape-Link -> Shape-In : ACK / bool inGate
    |||
    end
|||
Shape-In -> Shape-Link : End of measurement
Shape-Link -> Shape-In : ACK
deactivate Shape-Link
```

Datapackages are seriallized by QDataStream.
QDataStream is used in C++ by: 
```
QByteArray data;
QDataStream stream(&data, QIODevice::WriteOnly);
QVariant value = 3133.7;

stream << "String";
stream << value;
// and so on.. 
```
And in python:
```
data = QtCore.QByteArray()
stream = QtCore.QDataStream(data, QtCore.QIODevice.WriteOnly)
stream.writeString("GET")
stream.writeQVariant(QVariant(5.555))
```

Register Datafields:
```
stream
<< int64 msgId = -1      // code for new measurement
<< QVector<QString> scalarParametersHdf5Names   // HDF5 names for parameters contained in each event (area, deformation, etc..)
<< QVector<QString> vectorParametersHdf5Names   // names of vector parameters (traces)
<< QVector<QString> imageHdf5Name               // names of image data
```

Register Datafields ACK
```
stream
<< int64 ackId = -2
```

Data package:
```
stream
<< int64 eventId     // event id (unique inside measurement)
<< QVector<float> scalarParameters          // actual values for parameters
<< QVector<QVector<short>> vectorParameters // data for vector parameters (traces)
<< QVector<cv::Mat> // image data ??? maybe better as array
```

Data package response: 
```
stream
<< int64 eventId // for tracking
<< bool inGate // is event to be sorted or not?
// could be expanded
```

End of measurement:
```
stream << int64 eomId = -10
```

ACK end of measurement
```
stream << int64 eomAck = -11
```