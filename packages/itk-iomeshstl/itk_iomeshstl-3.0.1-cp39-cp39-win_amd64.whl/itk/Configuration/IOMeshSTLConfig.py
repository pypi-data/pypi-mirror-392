depends = ('ITKPyBase', 'ITKIOMeshBase', 'ITKCommon', )
templates = (  ('STLMeshIO', 'itk::STLMeshIO', 'itkSTLMeshIO', True),
  ('STLMeshIOFactory', 'itk::STLMeshIOFactory', 'itkSTLMeshIOFactory', True),
)
factories = (("MeshIO","STL"),)
