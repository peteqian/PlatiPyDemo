import SimpleITK as sitk
import numpy as np

def point2str(point, precision=1):
    """
    Format a point for printing, based on specified precision with trailing zeros. Uniform printing for vector-like data 
    (tuple, numpy array, list).
    
    Args:
        point (vector-like): nD point with floating point coordinates.
        precision (int): Number of digits after the decimal point.
    Return:
        String represntation of the given point "xx.xxx yy.yyy zz.zzz...".
    """
    return ' '.join(f'{c:.{precision}f}' for c in point)


def uniform_random_points(bounds, num_points):
    """
    Generate random (uniform withing bounds) nD point cloud. Dimension is based on the number of pairs in the bounds input.
    
    Args:
        bounds (list(tuple-like)): list where each tuple defines the coordinate bounds.
        num_points (int): number of points to generate.
    
    Returns:
        list containing num_points numpy arrays whose coordinates are within the given bounds.
    """
    internal_bounds = [sorted(b) for b in bounds]
         # Generate rows for each of the coordinates according to the given bounds, stack into an array, 
         # and split into a list of points.
    mat = np.vstack([np.random.uniform(b[0], b[1], num_points) for b in internal_bounds])
    return list(mat[:len(bounds)].T)


def target_registration_errors(tx, point_list, reference_point_list):
    """
    Distances between points transformed by the given transformation and their
    location in another coordinate system. When the points are only used to evaluate
    registration accuracy (not used in the registration) this is the target registration
    error (TRE).
    """
    return [np.linalg.norm(np.array(tx.TransformPoint(p)) -  np.array(p_ref))
          for p,p_ref in zip(point_list, reference_point_list)]


def print_transformation_differences(tx1, tx2):
    """
    Check whether two transformations are "equivalent" in an arbitrary spatial region 
    either 3D or 2D, [x=(-10,10), y=(-100,100), z=(-1000,1000)]. This is just a sanity check, 
    as we are just looking at the effect of the transformations on a random set of points in
    the region.
    """
    if tx1.GetDimension()==2 and tx2.GetDimension()==2:
        bounds = [(-10,10),(-100,100)]
    elif tx1.GetDimension()==3 and tx2.GetDimension()==3:
        bounds = [(-10,10),(-100,100), (-1000,1000)]
    else:
        raise ValueError('Transformation dimensions mismatch, or unsupported transformation dimensionality')
    num_points = 10
    point_list = uniform_random_points(bounds, num_points)
    tx1_point_list = [ tx1.TransformPoint(p) for p in point_list]
    differences = target_registration_errors(tx2, point_list, tx1_point_list)
    print(tx1.GetName()+ '-' +
          tx2.GetName()+
          f':\tminDifference: {min(differences):.2f} maxDifference: {max(differences):.2f}')


composite_transform = sitk.ReadTransform('TransformObject.tfm')
composite_transform = sitk.CompositeTransform(composite_transform)

# Print the composite_transform from the tfm file.
print(composite_transform)

# Retrieve the 1st Transform
transform_type = composite_transform.GetNthTransform(0)

# Downcast from Composite Transform to Euler3D Transform
euler3d_transform = transform_type.Downcast()
# print(euler3d_transform)

print('Type')
print(euler3d_transform.GetName())
print('Matrix')
print(euler3d_transform.GetMatrix())
print('Center')
print(euler3d_transform.GetCenter())
print('Translation')
print(euler3d_transform.GetTranslation())

# Retrieve the 2nd Transform
transform_type = composite_transform.GetNthTransform(1)

# Downcast from Composite Transform to VersorRigid3D Transform
versor_transform = transform_type.Downcast()
# print(versor_transform)

print('Type')
print(versor_transform.GetName())
print('Matrix')
print(versor_transform.GetMatrix())
print('Center')
print(versor_transform.GetCenter())
print('Translation')
print(versor_transform.GetTranslation())

# Create a Data Structure to store the Matrices

class TransformObject():
    def __init__(self, _transform_type, _matrix, _center, _translation):
        self.transform_type = _transform_type
        self.matrix = _matrix
        self.center = _center
        self.translation = _translation

# Attempt to store the matrices into a class
print('Storing the Transform Attributes to Object')
transObj = TransformObject(euler3d_transform.GetName(),
                            euler3d_transform.GetMatrix(),
                            euler3d_transform.GetCenter(),
                            euler3d_transform.GetTranslation())

print("################################# Trans Object ######################")
print(transObj.matrix)
print(transObj.center)
print(transObj.translation)

# Attempt to create a transform from the matrices
new_euler = sitk.Euler3DTransform()
new_euler.SetMatrix(transObj.matrix)
new_euler.SetCenter(transObj.center)
new_euler.SetTranslation(transObj.translation)

# Print the new Euler3DTransformation
print("################################# Printing New Euler ######################")
print(new_euler)

# Attempt to store the matrices into a class
print('Storing the Transform Attributes to Object')
transObj = TransformObject(versor_transform.GetName(),
                            versor_transform.GetMatrix(),
                            versor_transform.GetCenter(),
                            versor_transform.GetTranslation())

print("################################# Trans Object ######################")
print(transObj.matrix)
print(transObj.center)
print(transObj.translation)

# Attempt to create a transform from thversorrices
new_versor = sitk.VersorRigid3DTransform()
new_versor.SetMatrix(transObj.matrix)
new_versor.SetCenter(transObj.center)
new_versor.SetTranslation(transObj.translation)

# Print the new Euler3DTransformation
print("################################# Printing New Versor ######################")
print(new_versor)

print('Try this')

A0 = np.asarray(euler3d_transform.GetMatrix()).reshape(3,3)
c0 = np.asarray(euler3d_transform.GetCenter())
t0 = np.asarray(euler3d_transform.GetTranslation())

A1 = np.asarray(new_versor.GetMatrix()).reshape(3,3)
c1 = np.asarray(new_versor.GetCenter())
t1 = np.asarray(new_versor.GetTranslation())

combined_mat = np.dot(A0,A1)
combined_center = c1
combined_translation = np.dot(A0, t1+c1-c0) + t0+c0-c1
combined_affine = sitk.AffineTransform(combined_mat.flatten(), 
                                        combined_translation, 
                                        combined_center)

# Check if the two transformations are equivalent.
# https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/blob/master/Python/22_Transforms.ipynb
# https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/blob/master/Python/65_Registration_FFD.ipynb

print('Apply the two transformations to the same point cloud:')
print('\t', end='')
print_transformation_differences(composite_transform, combined_affine)

print('Transform parameters:')
print('\tComposite transform: ' + point2str(composite_transform.GetParameters(),2))
print('\tCombined affine: ' + point2str(combined_affine.GetParameters(),2))

print('Fixed parameters:')
print('\tComposite transform: ' + point2str(composite_transform.GetFixedParameters(),2))
print('\tCombined affine: ' + point2str(combined_affine.GetFixedParameters(),2))

print('combined_affine')
print(combined_affine)

# https://discourse.itk.org/t/express-affinetransform-as-single-4x4-matrix/3193/5

A = np.array(combined_affine.GetMatrix()).reshape(3,3)
c = np.array(combined_affine.GetCenter())
t = np.array(combined_affine.GetTranslation())
overall = np.eye(4)
overall[0:3,0:3] = A
overall[0:3,3] = -np.dot(A,c)+t+c

# pnt = [10,3,4]

# print(combined_affine.TransformPoint(pnt))
# print(np.dot(overall,pnt+[1]))

print(overall)