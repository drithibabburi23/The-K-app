import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/product.dart';

class ApiException implements Exception {
  const ApiException(this.message);
  final String message;
  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({String? baseUrl}) : baseUrl = (baseUrl ?? const String.fromEnvironment('API_BASE_URL', defaultValue: 'https://the-k-app-1.onrender.com')).replaceAll(RegExp(r'/$'), '');

  final String baseUrl;
  String? token;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Future<dynamic> _request(String method, String path, {Object? body}) async {
    final uri = Uri.parse('$baseUrl$path');
    final request = http.Request(method, uri)..headers.addAll(_headers);
    if (body != null) request.body = jsonEncode(body);
    try {
      final response = await http.Client().send(request);
      final payload = await response.stream.bytesToString();
      final data = payload.isEmpty ? <String, dynamic>{} : jsonDecode(payload) as Map<String, dynamic>;
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw ApiException('${data['detail'] ?? data['message'] ?? 'Request failed'} (${response.statusCode})');
      }
      return data;
    } on ApiException {
      rethrow;
    } catch (_) {
      throw const ApiException('Unable to reach KarigarConnect. Check your connection and try again.');
    }
  }

  Future<Map<String, dynamic>> authenticate({required String name, required String email, required String password, required String role, required bool register}) async {
    final data = await _request(register ? 'POST' : 'POST', register ? '/api/v1/auth/register' : '/api/v1/auth/login', body: register ? {'name': name, 'email': email, 'password': password, 'role': role} : {'email': email, 'password': password}) as Map<String, dynamic>;
    token = data['access_token'] as String;
    return data['user'] as Map<String, dynamic>;
  }

  Future<List<Product>> products({String search = '', bool mine = false}) async {
    final query = <String, String>{if (search.trim().isNotEmpty) 'search': search.trim(), if (mine) 'mine': 'true'};
    final suffix = query.isEmpty ? '' : '?${Uri(queryParameters: query).query}';
    final data = await _request('GET', '/api/v1/products$suffix');
    return data is List ? data.map((item) => Product.fromJson(item as Map<String, dynamic>)).toList() : <Product>[];
  }

  Future<Map<String, dynamic>> catalog(String text) async => await _request('POST', '/api/v1/catalog', body: {'text': text}) as Map<String, dynamic>;

  Future<Product> createProduct({required String title, required String description, required String material, required String craftType, required double price, required bool published}) async {
    final data = await _request('POST', '/api/v1/products', body: {'title': title, 'description': description, 'material': material, 'craft_type': craftType, 'price': price, 'status': published ? 'published' : 'draft'}) as Map<String, dynamic>;
    return Product.fromJson(data);
  }

  Future<List<Map<String, dynamic>>> enquiries() async {
    final data = await _request('GET', '/api/v1/enquiries');
    return (data as List).cast<Map<String, dynamic>>();
  }

  Future<void> createEnquiry(int productId, String message) async {
    await _request('POST', '/api/v1/enquiries', body: {'product_id': productId, 'message': message});
  }

  Future<void> updateEnquiry(int id, String status) async {
    await _request('PATCH', '/api/v1/enquiries/$id', body: {'status': status});
  }
}