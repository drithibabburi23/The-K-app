import '../models/product.dart';

class CatalogService {
  Future<Product> generateFromText(String text) async {
    final cleanText = text.trim();
    if (cleanText.isEmpty) {
      throw const FormatException('Please describe your product first.');
    }

    return Product(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      name: _guessName(cleanText),
      category: _guessCategory(cleanText),
      description: cleanText,
      price: 0,
      status: SyncStatus.local,
    );
  }

  String _guessName(String text) {
    final words = text.split(RegExp(r'\s+')).take(4).join(' ');
    return words[0].toUpperCase() + words.substring(1);
  }

  String _guessCategory(String text) {
    final value = text.toLowerCase();
    if (value.contains('saree') || value.contains('cloth') || value.contains('weave')) {
      return 'Textiles';
    }
    if (value.contains('pot') || value.contains('clay')) {
      return 'Pottery';
    }
    if (value.contains('wood') || value.contains('carve')) {
      return 'Woodcraft';
    }
    return 'Handicrafts';
  }
}