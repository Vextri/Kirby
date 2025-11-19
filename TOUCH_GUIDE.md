# Kirby Touch Weather Display - Usage Guide

## 🌸 **New Touch-Friendly Design**

### **Main Features:**
1. **Full-Screen Art Focus** - Kirby takes center stage, changes with weather
2. **Swipe Navigation** - Swipe right to see messages, left to go back  
3. **Unread Notifications** - Red badge shows unread message count
4. **Minimal Resource Usage** - 30 FPS, efficient rendering

### **How to Use:**

#### **Mouse/Desktop:**
- **Click and drag right** → Opens messages panel
- **Click and drag left** → Closes messages panel  
- **Arrow keys** → Right/Left to navigate
- **R key** → Refresh data
- **N key** → Simulate new message (for testing)
- **ESC** → Exit

#### **Touch Screen (Future):**
- **Swipe right** → Opens messages
- **Swipe left** → Closes messages
- **Tap notification badge** → Opens messages

### **Visual Elements:**

#### **Main Art View:**
- **Large Kirby image** centered on screen
- **Weather info** at bottom (temp, condition, time)
- **Swipe hint** in top-right corner
- **Notification badge** if unread messages

#### **Messages Panel:**
- **Slides in from right** with smooth animation
- **Shows up to 6 recent messages**
- **Each message has sender name**
- **Swipe hint to close**

### **Resource Efficiency:**
- **30 FPS** instead of 60 (50% less CPU)
- **Simple gradients** instead of complex effects  
- **Cached fonts** loaded once
- **Minimal animation** during idle
- **Efficient sliding** with surface blitting

### **Perfect for:**
- **Kiosk displays**
- **Tablet interfaces** 
- **Touch screen monitors**
- **Low-power devices**
- **Raspberry Pi displays**

### **Controls Summary:**
```
Main View → Swipe/Drag Right → Messages View
Messages View → Swipe/Drag Left → Main View

Keyboard shortcuts:
- Right Arrow = Open messages
- Left Arrow = Close messages  
- R = Refresh data
- N = Simulate new message (testing)
- ESC = Exit
```

The interface prioritizes the **art experience** while keeping messages easily accessible but not distracting from the main Kirby display! 🌸✨
