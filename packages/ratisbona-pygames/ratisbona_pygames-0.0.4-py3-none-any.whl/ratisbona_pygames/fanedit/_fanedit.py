import math
import sys
from math import cos, sin, pi

from PyQt6.QtCore import QRectF, QPointF, Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QFileDialog, QGraphicsItem, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QPixmap, QAction, QPen, QBrush, QColor, QPainter, QPainterPath


class Segment(QGraphicsItem):
    """A single segment with spacing and a white outline."""

    def __init__(self, center_point: QPointF, radius_start: float, radius_end: float, angle_start: float, angle_end: float):
        super().__init__()
        QGraphicsItem.__init__(self)

        self.center_point = center_point
        self.radius_start = radius_start
        self.radius_end = radius_end
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.filled = False

        # Calculate the start and end points for both radii
        start_rad = self.angle_start
        end_rad = self.angle_end

        # Points for the inner arc
        self.inner_start = QPointF(
            self.center_point.x() - self.radius_start * math.sin(start_rad),
            self.center_point.y() + self.radius_start * math.cos(start_rad)
        )
        self.inner_end = QPointF(
            self.center_point.x() - self.radius_start * math.sin(end_rad),
            self.center_point.y() + self.radius_start * math.cos(end_rad)
        )

        # Points for the outer arc
        self.outer_start = QPointF(
            self.center_point.x() - self.radius_end * math.sin(start_rad),
            self.center_point.y() + self.radius_end * math.cos(start_rad)
        )
        self.outer_end = QPointF(
            self.center_point.x() - self.radius_end * math.sin(end_rad),
            self.center_point.y() + self.radius_end * math.cos(end_rad)
        )

    def boundingRect(self):
        """Defines the bounding box of the segment."""
        min_x = min(self.inner_start.x(), self.inner_end.x(), self.outer_start.x(), self.outer_end.x())
        min_y = min(self.inner_start.y(), self.inner_end.y(), self.outer_start.y(), self.outer_end.y())
        max_x = max(self.inner_start.x(), self.inner_end.x(), self.outer_start.x(), self.outer_end.x())
        max_y = max(self.inner_start.y(), self.inner_end.y(), self.outer_start.y(), self.outer_end.y())
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def paint(self, painter: QPainter, option, widget):
        """Draws the segment with two arcs and two connecting lines."""
        pen = QPen(Qt.GlobalColor.white, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.GlobalColor.transparent if not self.filled else Qt.GlobalColor.red)

        path = QPainterPath()

        # Move to start of inner arc
        path.moveTo(self.outer_start)
        path.lineTo(self.outer_end)
        path.lineTo(self.inner_end)
        path.lineTo(self.inner_start)
        path.lineTo(self.outer_start)

        # Draw the final shape
        painter.drawPath(path)

    def mousePressEvent(self, event):
        self.filled = not self.filled
        self.update()
        event.accept()


class CircularEditor(QGraphicsScene):
    """Main scene that contains the circular segmented editor."""

    def __init__(self, width, height):
        super().__init__(0, 0, width, height)
        self.center = QPointF(width / 2, height / 2)
        self.inner_radius = 50  # Half of the empty hub (100px)
        self.outer_radius = min(width, height) / 2 - 50  # Overall size of the circle
        self.num_segments = 144
        self.radial_segments = 11
        self.create_segments()

    def remove_connections(self):
        for item in self.items():
            item.clicked.disconnect()

    def resizeEvent(self, event):
        print("Resize", event)
        """Resize the scene dynamically when the window changes size."""
        new_size = min(self.width(), self.height())
        self.clear()
        self.setSceneRect(0, 0, new_size, new_size)
        self.center = QPointF(new_size / 2, new_size / 2)
        self.outer_radius = new_size / 2 - 50
        self.create_segments()

    def create_segments(self):
        """Generate the circular grid segments."""
        angle_step = 1.8 * pi / self.num_segments
        radial_step = (self.outer_radius - self.inner_radius) / self.radial_segments

        for axial_segment_num in range(self.num_segments):
            phi_segment_start = axial_segment_num * angle_step + angle_step / 4 + 0.1 * pi
            for radial_segment_num in range(self.radial_segments):
                r_segment_start = self.inner_radius + radial_segment_num * radial_step
                segment = Segment(self.center, r_segment_start, r_segment_start + radial_step / 2, phi_segment_start, phi_segment_start + angle_step / 2)
                self.addItem(segment)



class ImageEditor(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circular Editor")
        self.setGeometry(100, 100, 1024, 768)

        # Create central widget with layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full scaling

        # Create graphics view
        self.scene = CircularEditor(1024, 768)  # Start with initial size
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints() | self.view.renderHints().Antialiasing)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Keep it centered
        layout.addWidget(self.view)  # Add view to layout

        self.resizeEvent(None)  # Initial resize

    def resizeEvent(self, event):
        """Resize the scene dynamically when the window changes size."""
        new_size = min(self.width(), self.height())  # Keep it square
        self.scene.setSceneRect(0, 0, new_size, new_size)  # Resize scene
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.scene.resizeEvent(None)


    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # New Action
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_canvas)
        file_menu.addAction(new_action)

        # Load Action
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_image)
        file_menu.addAction(load_action)

        # Save Action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        # Quit Action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def new_canvas(self):
        """Clears the canvas."""
        self.scene.clear()

    def load_image(self):
        """Loads an image onto the canvas."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.scene.clear()
            self.scene.addPixmap(pixmap)

    def save_image(self):
        """Saves the current scene as an image (not implemented yet)."""
        print("Save functionality not implemented yet")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageEditor()
    window.show()
    sys.exit(app.exec())
