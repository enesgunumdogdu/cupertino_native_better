// iOS probe for #184: a CNSearchBar whose frame overlaps the home-indicator
// safe area must draw its field centred in that frame, like a bar that
// overlaps nothing.
//
//   flutter build ios --simulator --debug -t lib/issue184_probe_entry.dart
//
// Two 48 pt bars on a black page, each over a magenta box of its exact
// frame: "reference" at the top, "overlap" flush with the screen's bottom
// edge, so the bottom 34 pt of its frame is in the home-indicator area.
// The bars have a white field, so tool/issue184_measure.py can find the
// field in a simulator screenshot and compare its centre with the frame's.

import 'package:cupertino_native_better/cupertino_native_better.dart';
import 'package:flutter/cupertino.dart';

const double kBarHeight = 48;
const double kReferenceTop = 300;
const Color kFrameColor = Color(0xFFFF00FF);

void main() {
  runApp(
    const CupertinoApp(
      debugShowCheckedModeBanner: false,
      theme: CupertinoThemeData(brightness: Brightness.dark),
      home: _ProbePage(),
    ),
  );
}

class _ProbePage extends StatelessWidget {
  const _ProbePage();

  @override
  Widget build(BuildContext context) {
    return const CupertinoPageScaffold(
      backgroundColor: Color(0xFF000000),
      resizeToAvoidBottomInset: false,
      child: Stack(
        children: [
          Positioned(
            top: kReferenceTop,
            left: 0,
            right: 0,
            height: kBarHeight,
            child: _ProbeBar(),
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            height: kBarHeight,
            child: _ProbeBar(),
          ),
        ],
      ),
    );
  }
}

class _ProbeBar extends StatelessWidget {
  const _ProbeBar();

  @override
  Widget build(BuildContext context) {
    return const ColoredBox(
      color: kFrameColor,
      child: CNSearchBar(
        expandable: false,
        expandedHeight: kBarHeight,
        showShadow: false,
        showCancelButton: false,
        backgroundColor: Color(0xFFFFFFFF),
        placeholder: '',
      ),
    );
  }
}
