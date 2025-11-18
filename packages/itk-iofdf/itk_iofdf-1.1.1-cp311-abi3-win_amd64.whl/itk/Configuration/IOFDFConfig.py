depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('FDFImageIO', 'itk::FDFImageIO', 'itkFDFImageIO', True),
  ('FDFImageIOFactory', 'itk::FDFImageIOFactory', 'itkFDFImageIOFactory', True),
)
factories = (("ImageIO","FDF"),)
