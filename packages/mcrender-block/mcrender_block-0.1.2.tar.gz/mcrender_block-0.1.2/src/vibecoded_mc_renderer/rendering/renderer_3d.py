"""3D OpenGL-based isometric block renderer using ModernGL."""

import moderngl
import numpy as np
from PIL import Image
import pyrr


class BlockRenderer3D:
    """OpenGL-based 3D block renderer for perfect isometric projection."""
    
    def __init__(self, output_size: int = 128, camera_height: float = 1.5, samples: int = 4):
        """
        Initialize the 3D renderer.
        
        Args:
            output_size: Size of output images
            camera_height: Camera Y position (1.0=acute/sharp, 1.5=standard, 2.0=wide/top-down)
            samples: MSAA samples for anti-aliasing (0=off, 2/4/8/16=quality)
        """
        self.output_size = output_size
        self.camera_height = camera_height
        self.samples = samples
        
        # Create OpenGL context (standalone, no window needed)
        self.ctx = moderngl.create_standalone_context()
        
        # Vertex shader - transforms vertices
        vertex_shader = """
        #version 330
        
        in vec3 in_position;
        in vec2 in_texcoord;
        
        out vec2 v_texcoord;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        void main() {
            gl_Position = projection * view * model * vec4(in_position, 1.0);
            v_texcoord = in_texcoord;
        }
        """
        
        # Fragment shader - applies textures
        fragment_shader = """
        #version 330
        
        in vec2 v_texcoord;
        out vec4 fragColor;
        
        uniform sampler2D texture0;
        uniform float shade;
        
        void main() {
            vec4 color = texture(texture0, v_texcoord);
            fragColor = vec4(color.rgb * shade, color.a);
        }
        """
        
        # Compile shader program
        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )
        
        # Create framebuffers for offscreen rendering with optional MSAA
        if samples > 0:
            # Multisample framebuffer for anti-aliasing
            self.msaa_fbo = self.ctx.framebuffer(
                color_attachments=[
                    self.ctx.texture((output_size, output_size), 4, samples=samples)
                ],
                depth_attachment=self.ctx.depth_renderbuffer((output_size, output_size), samples=samples)
            )
            # Regular FBO for final resolved output
            self.fbo = self.ctx.framebuffer(
                color_attachments=[
                    self.ctx.texture((output_size, output_size), 4)
                ]
            )
        else:
            self.msaa_fbo = None
            self.fbo = self.ctx.framebuffer(
                color_attachments=[
                    self.ctx.texture((output_size, output_size), 4)
                ],
                depth_attachment=self.ctx.depth_renderbuffer((output_size, output_size))
            )
        
        # Enable features
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Setup isometric camera
        self._setup_camera()
        
        # Create cube geometry
        self._create_cube()
    
    def _setup_camera(self):
        """Setup isometric camera view."""
        # Isometric view: rotate 45° around Y, then ~35.264° around X
        # Use orthographic projection for true isometric (no perspective)
        
        # View matrix: position camera for isometric view
        # camera_height controls the viewing angle:
        #   1.0 = acute/sharp angle (more side view)
        #   1.5 = standard isometric (default)
        #   2.0 = wide angle (more top-down view)
        eye = pyrr.Vector3([1.5, self.camera_height, 1.5])
        target = pyrr.Vector3([0.0, 0.0, 0.0])
        up = pyrr.Vector3([0.0, 1.0, 0.0])
        self.view = pyrr.matrix44.create_look_at(eye, target, up)
        
        # Orthographic projection (no perspective distortion)
        # Adjust bounds to fit cube nicely in frame
        size = 1.2
        self.projection = pyrr.matrix44.create_orthogonal_projection(
            -size, size, -size, size, 0.1, 10.0
        )
    
    def _create_cube(self):
        """Create cube geometry with texture coordinates."""
        # Cube vertices (8 corners)
        # Centered at origin, size 1x1x1
        vertices = np.array([
            # Position (x,y,z), TexCoord (u,v)
            # Front face (Z+)
            -0.5, -0.5,  0.5,  0.0, 1.0,
             0.5, -0.5,  0.5,  1.0, 1.0,
             0.5,  0.5,  0.5,  1.0, 0.0,
            -0.5,  0.5,  0.5,  0.0, 0.0,
            
            # Back face (Z-)
            -0.5, -0.5, -0.5,  1.0, 1.0,
            -0.5,  0.5, -0.5,  1.0, 0.0,
             0.5,  0.5, -0.5,  0.0, 0.0,
             0.5, -0.5, -0.5,  0.0, 1.0,
            
            # Top face (Y+)
            -0.5,  0.5, -0.5,  0.0, 0.0,
            -0.5,  0.5,  0.5,  0.0, 1.0,
             0.5,  0.5,  0.5,  1.0, 1.0,
             0.5,  0.5, -0.5,  1.0, 0.0,
            
            # Bottom face (Y-)
            -0.5, -0.5, -0.5,  0.0, 1.0,
             0.5, -0.5, -0.5,  1.0, 1.0,
             0.5, -0.5,  0.5,  1.0, 0.0,
            -0.5, -0.5,  0.5,  0.0, 0.0,
            
            # Right face (X+)
             0.5, -0.5, -0.5,  1.0, 1.0,
             0.5,  0.5, -0.5,  1.0, 0.0,
             0.5,  0.5,  0.5,  0.0, 0.0,
             0.5, -0.5,  0.5,  0.0, 1.0,
            
            # Left face (X-)
            -0.5, -0.5, -0.5,  0.0, 1.0,
            -0.5, -0.5,  0.5,  1.0, 1.0,
            -0.5,  0.5,  0.5,  1.0, 0.0,
            -0.5,  0.5, -0.5,  0.0, 0.0,
        ], dtype='f4')
        
        # Indices for triangles (2 triangles per face)
        indices = np.array([
            0,  1,  2,   2,  3,  0,   # Front
            4,  5,  6,   6,  7,  4,   # Back
            8,  9, 10,  10, 11,  8,   # Top
            12, 13, 14,  14, 15, 12,  # Bottom
            16, 17, 18,  18, 19, 16,  # Right
            20, 21, 22,  22, 23, 20,  # Left
        ], dtype='i4')
        
        # Create vertex buffer
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.ibo = self.ctx.buffer(indices.tobytes())
        
        # Create vertex array object
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.vbo, '3f 2f', 'in_position', 'in_texcoord'),
            ],
            index_buffer=self.ibo
        )
    
    def render_cube(
        self,
        top_texture: Image.Image,
        left_texture: Image.Image,
        right_texture: Image.Image,
    ) -> Image.Image:
        """
        Render a cube with different textures on visible faces.
        
        Args:
            top_texture: Texture for top face
            left_texture: Texture for left face  
            right_texture: Texture for right/front face
            
        Returns:
            Rendered image
        """
        # Use MSAA framebuffer if available, otherwise regular FBO
        if self.msaa_fbo:
            self.msaa_fbo.use()
        else:
            self.fbo.use()
        
        # Clear with transparency
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        
        # Set common matrices
        model = pyrr.matrix44.create_identity()
        self.program['model'].write(model.astype('f4').tobytes())
        self.program['view'].write(self.view.astype('f4').tobytes())
        self.program['projection'].write(self.projection.astype('f4').tobytes())
        
        # Create textures from PIL images
        top_tex = self._create_texture(top_texture)
        left_tex = self._create_texture(left_texture)
        right_tex = self._create_texture(right_texture)
        
        # Render each visible face separately with appropriate texture and shading
        # In isometric view from (1.5, 1.5, 1.5), we see: Y+ (top), X+ (right), Z+ (front)
        # left_texture = side texture (goes to Z+ face, appears on left in view)
        # right_texture = front texture (goes to X+ face, appears on right in view)
        
        # Render top face (Y+) - brightest
        top_tex.use(0)
        self.program['texture0'] = 0
        self.program['shade'] = 1.0
        self._render_face('top')
        
        # Render front face (Z+) - side texture, medium shade (appears on left in isometric view)
        left_tex.use(0)
        self.program['shade'] = 0.8
        self._render_face('front')
        
        # Render right face (X+) - front texture, light shade (appears on right in isometric view)
        right_tex.use(0)
        self.program['shade'] = 0.9
        self._render_face('right')
        
        # Resolve MSAA to regular framebuffer if needed
        if self.msaa_fbo:
            self.ctx.copy_framebuffer(self.fbo, self.msaa_fbo)
        
        # Read pixels from framebuffer
        data = self.fbo.read(components=4, alignment=1)
        
        # Convert to PIL Image
        img = Image.frombytes('RGBA', (self.output_size, self.output_size), data)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # OpenGL has Y-up
        
        # Cleanup textures
        top_tex.release()
        left_tex.release()
        right_tex.release()
        
        return img
    
    def _render_face(self, face: str):
        """Render a specific face of the cube."""
        # Map face names to index ranges
        face_indices = {
            'front': (0, 6),    # Front face (Z+): indices 0-5
            'back': (6, 12),    # Back face (Z-): indices 6-11
            'top': (12, 18),    # Top face (Y+): indices 12-17
            'bottom': (18, 24), # Bottom face (Y-): indices 18-23
            'right': (24, 30),  # Right face (X+): indices 24-29
            'left': (30, 36),   # Left face (X-): indices 30-35
        }
        
        start, end = face_indices[face]
        count = end - start
        
        # Render subset of indices
        self.vao.render(mode=moderngl.TRIANGLES, vertices=count, first=start)
    
    def _create_texture(self, pil_image: Image.Image) -> moderngl.Texture:
        """Convert PIL Image to OpenGL texture."""
        img = pil_image.convert('RGBA')
        
        texture = self.ctx.texture(img.size, 4, img.tobytes())
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        
        return texture
    
    def cleanup(self):
        """Release OpenGL resources."""
        self.vao.release()
        self.vbo.release()
        self.ibo.release()
        if self.msaa_fbo:
            self.msaa_fbo.release()
        self.fbo.release()
        self.program.release()
        self.ctx.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
