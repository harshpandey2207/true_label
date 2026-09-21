import 'package:flutter/material.dart';

class BoundingBoxPainter extends CustomPainter {
  final List<dynamic> declarations;
  final double imageWidth;
  final double imageHeight;

  BoundingBoxPainter({
    required this.declarations,
    required this.imageWidth,
    required this.imageHeight,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final double scaleX = size.width / imageWidth;
    final double scaleY = size.height / imageHeight;

    for (var item in declarations) {
      final bool isCompliant = item['is_compliant'];
      final List<dynamic> box = item['box']; 

      final paint = Paint()
        ..color = isCompliant ? Colors.greenAccent : Colors.redAccent
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.0;

      final fillPaint = Paint()
        ..color = (isCompliant ? Colors.greenAccent : Colors.redAccent).withValues(alpha: 0.2)
        ..style = PaintingStyle.fill;

      final path = Path();
      path.moveTo(box[0][0] * scaleX, box[0][1] * scaleY);
      path.lineTo(box[1][0] * scaleX, box[1][1] * scaleY);
      path.lineTo(box[2][0] * scaleX, box[2][1] * scaleY);
      path.lineTo(box[3][0] * scaleX, box[3][1] * scaleY);
      path.close();

      canvas.drawPath(path, fillPaint);
      canvas.drawPath(path, paint);

      final textSpan = TextSpan(
        text: '${item['tag']} (${item['height_mm']}mm)',
        style: TextStyle(
          color: isCompliant ? Colors.greenAccent : Colors.redAccent,
          fontSize: 14,
          fontWeight: FontWeight.bold,
          backgroundColor: Colors.black54,
        ),
      );
      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();
      textPainter.paint(canvas, Offset(box[0][0] * scaleX, (box[0][1] * scaleY) - 20));
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}