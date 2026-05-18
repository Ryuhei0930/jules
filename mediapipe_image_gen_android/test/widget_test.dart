import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mediapipe_image_gen_android/main.dart';

void main() {
  testWidgets('App renders correctly smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());

    // Verify that the title is rendered.
    expect(find.text('MediaPipe Local Image Gen'), findsOneWidget);

    // Verify that the text field is present.
    expect(find.byType(TextField), findsOneWidget);

    // Verify that the button is present.
    expect(find.text('画像を生成する'), findsOneWidget);
  });
}
