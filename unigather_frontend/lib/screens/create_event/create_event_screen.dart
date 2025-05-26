import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:unigather_frontend/widgets/bottom_nav_bar.dart';

class CreateEventScreen extends StatefulWidget {
  const CreateEventScreen({super.key});

  @override
  State<CreateEventScreen> createState() => _CreateEventScreenState();
}

class _CreateEventScreenState extends State<CreateEventScreen> {
  final _formKey = GlobalKey<FormState>();

  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descController = TextEditingController();
  final TextEditingController _locationController = TextEditingController();
  final TextEditingController _visibilityController = TextEditingController();

  DateTime? _selectedDateTime;

  @override
  Widget build(BuildContext context) {
    final Color uniRed = const Color.fromARGB(255, 124, 0, 0);

    return Scaffold(
      backgroundColor: uniRed,
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: const Text(
          'UniGather',
          style: TextStyle(
            color: Colors.black,
            fontFamily: 'Roboto',
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        centerTitle: true,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          elevation: 6,
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Stack(
                  children: [
                    ClipRRect(
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(16),
                        topRight: Radius.circular(16),
                      ),
                      child: Image.asset(
                        'assets/images/header.png',
                        width: double.infinity,
                        height: 200,
                        fit: BoxFit.cover,
                      ),
                    ),
                    Positioned(
                      bottom: 16,
                      left: 16,
                      right: 16,
                      child: Container(
                        height: 60,
                        decoration: BoxDecoration(
                          color: Colors.grey[300],
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Center(
                          child: Text(
                            'Gallery Placeholder',
                            style: TextStyle(
                              color: Colors.black54,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),

                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      TextFormField(
                        controller: _titleController,
                        decoration: const InputDecoration(
                          labelText: 'Event Title',
                        ),
                        validator:
                            (value) => value!.isEmpty ? 'Enter a title' : null,
                      ),
                      TextFormField(
                        controller: _descController,
                        decoration: const InputDecoration(
                          labelText: 'Description',
                        ),
                        maxLines: 3,
                      ),
                      TextFormField(
                        controller: _locationController,
                        decoration: const InputDecoration(
                          labelText: 'Location',
                        ),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          const Icon(Icons.calendar_today, size: 20),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              _selectedDateTime == null
                                  ? 'Choose Date & Time'
                                  : DateFormat(
                                    'EEEE, MMM d · HH:mm',
                                  ).format(_selectedDateTime!),
                            ),
                          ),
                          TextButton(
                            onPressed: _pickDateTime,
                            child: const Text('Select'),
                          ),
                        ],
                      ),
                      TextFormField(
                        controller: _visibilityController,
                        decoration: const InputDecoration(
                          labelText: 'Visibility (e.g. public/private)',
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton.icon(
                        onPressed: _submitForm,
                        icon: const Icon(Icons.check),
                        label: const Text("Create Event"),
                        style: ElevatedButton.styleFrom(
                          minimumSize: const Size(double.infinity, 45),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 3, // set this per screen (0=profile, 1=explore, etc.)
        onTap: (index) {
          switch (index) {
            case 0:
              Navigator.pushNamed(context, '/profile');
              break;
            case 1:
              Navigator.pushNamed(context, '/explore');
              break;
            case 2:
              Navigator.pushNamed(context, '/nearby');
              break;
            case 3:
              Navigator.pushNamed(context, '/create');
              break;
          }
        },
      ),
    );
  }

  Future<void> _pickDateTime() async {
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime(2100),
    );

    if (date == null) return;

    final time = await showTimePicker(
      context: context,
      initialTime: const TimeOfDay(hour: 19, minute: 0),
    );

    if (time == null) return;

    setState(() {
      _selectedDateTime = DateTime(
        date.year,
        date.month,
        date.day,
        time.hour,
        time.minute,
      );
    });
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      // TODO: Handle API submission or local state update
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Event created (mock)')));
    }
  }
}
