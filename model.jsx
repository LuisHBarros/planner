import React, { useState, useRef, useEffect } from 'react';
import { Calendar, Users, AlertTriangle, Clock, ArrowRight, GitBranch, Plus, X, Check } from 'lucide-react';

export default function PlannerMultiplayer() {
  const [tasks, setTasks] = useState([
    {
      id: 'task-1',
      title: 'Develop API Endpoints',
      role: 'Backend',
      status: 'ready',
      expectedStart: '2026-12-24',
      expectedEnd: '2026-12-24',
      actualStart: null,
      actualEnd: null,
      dependencies: [],
      assignee: 'John Smith',
      estimatedHours: 8,
      startColumn: 0,
      endColumn: 0
    },
    {
      id: 'task-2',
      title: 'Create Login UI',
      role: 'Frontend',
      status: 'blocked',
      expectedStart: '2026-12-25',
      expectedEnd: '2026-12-25',
      actualStart: null,
      actualEnd: null,
      dependencies: ['task-1'],
      assignee: 'Sarah Chen',
      estimatedHours: 6,
      startColumn: 1,
      endColumn: 1
    },
    {
      id: 'task-3',
      title: 'Database Migration & Optimization',
      role: 'Backend',
      status: 'ready',
      expectedStart: '2026-12-24',
      expectedEnd: '2026-12-28',
      actualStart: null,
      actualEnd: null,
      dependencies: [],
      assignee: 'Maria Garcia',
      estimatedHours: 40,
      startColumn: 0,
      endColumn: 4
    },
    {
      id: 'task-4',
      title: 'Refine U/UX',
      role: 'Designer',
      status: 'blocked',
      expectedStart: '2026-12-25',
      expectedEnd: '2026-12-26',
      actualStart: null,
      actualEnd: null,
      dependencies: ['task-1'],
      assignee: 'Alex Rivera',
      estimatedHours: 12,
      startColumn: 1,
      endColumn: 2
    },
    {
      id: 'task-5',
      title: 'Implement Payment Gateway',
      role: 'Backend',
      status: 'blocked',
      expectedStart: '2026-12-27',
      expectedEnd: '2026-12-27',
      actualStart: null,
      actualEnd: null,
      dependencies: ['task-2'],
      assignee: 'John Smith',
      estimatedHours: 12,
      startColumn: 3,
      endColumn: 3
    }
  ]);

  const [selectedTask, setSelectedTask] = useState(null);
  const [showDependencies, setShowDependencies] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [newTask, setNewTask] = useState({
    title: '',
    role: 'Backend',
    expectedStart: '2026-12-24',
    expectedEnd: '2026-12-24',
    assignee: '',
    estimatedHours: 8,
    dependencies: []
  });
  const gridRef = useRef(null);
  const taskRefs = useRef({});
  const [, forceUpdate] = useState({});

  // Zoom with Ctrl + mouse wheel
  useEffect(() => {
    const handleWheel = (e) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        setZoom(prev => Math.min(Math.max(prev + delta, 0.5), 2));
      }
    };

    window.addEventListener('wheel', handleWheel, { passive: false });
    return () => window.removeEventListener('wheel', handleWheel);
  }, []);

  const roleConfig = {
    Backend: {
      primary: '#D97706',
      secondary: '#FEF3C7',
      dark: '#92400E',
      icon: '⚙️'
    },
    Frontend: {
      primary: '#059669',
      secondary: '#D1FAE5',
      dark: '#065F46',
      icon: '🎨'
    },
    Designer: {
      primary: '#2563EB',
      secondary: '#DBEAFE',
      dark: '#1E40AF',
      icon: '✨'
    }
  };

  const statusConfig = {
    ready: { label: 'READY', color: '#10B981', bg: '#D1FAE5', border: '#059669' },
    blocked: { label: 'BLOCKED', color: '#FFFFFF', bg: '#EF4444', border: '#DC2626' },
    in_progress: { label: 'IN PROGRESS', color: '#92400E', bg: '#FCD34D', border: '#F59E0B' },
    done: { label: 'DONE', color: '#6B7280', bg: '#E5E7EB', border: '#9CA3AF' }
  };

  const days = [
    { day: 'Tue', date: 24, label: 'Dec 24', value: '2026-12-24' },
    { day: 'Wed', date: 25, label: 'Dec 25', value: '2026-12-25' },
    { day: 'Thu', date: 26, label: 'Dec 26', value: '2026-12-26' },
    { day: 'Fri', date: 27, label: 'Dec 27', value: '2026-12-27' },
    { day: 'Sat', date: 28, label: 'Dec 28', value: '2026-12-28' }
  ];

  const getDependentTasks = (taskId) => {
    return tasks.filter(t => t.dependencies.includes(taskId));
  };

  const getColumnFromDate = (dateStr) => {
    return days.findIndex(d => d.value === dateStr);
  };

  // Calculate row positions to prevent overlap
  const calculateTaskRows = () => {
    const rowMap = {};
    
    const sortedTasks = [...tasks].sort((a, b) => {
      if (a.startColumn !== b.startColumn) return a.startColumn - b.startColumn;
      return a.endColumn - b.endColumn;
    });
    
    sortedTasks.forEach(task => {
      const taskSpan = { start: task.startColumn, end: task.endColumn };
      let assignedRow = 0;
      
      while (true) {
        let hasOverlap = false;
        
        for (const [otherId, otherRow] of Object.entries(rowMap)) {
          if (otherRow !== assignedRow) continue;
          
          const otherTask = tasks.find(t => t.id === otherId);
          if (!otherTask) continue;
          
          const otherSpan = { start: otherTask.startColumn, end: otherTask.endColumn };
          
          if (!(taskSpan.end < otherSpan.start || taskSpan.start > otherSpan.end)) {
            hasOverlap = true;
            break;
          }
        }
        
        if (!hasOverlap) {
          rowMap[task.id] = assignedRow;
          break;
        }
        
        assignedRow++;
      }
    });
    
    return rowMap;
  };

  const taskRowAssignments = calculateTaskRows();

  useEffect(() => {
    const timer = setTimeout(() => {
      forceUpdate({});
    }, 100);
    return () => clearTimeout(timer);
  }, [tasks, zoom]);

  const createTask = () => {
    const startCol = getColumnFromDate(newTask.expectedStart);
    const endCol = getColumnFromDate(newTask.expectedEnd);
    
    if (startCol === -1 || endCol === -1 || startCol > endCol) {
      alert('Invalid date range');
      return;
    }

    const task = {
      id: `task-${Date.now()}`,
      ...newTask,
      status: newTask.dependencies.length > 0 ? 'blocked' : 'ready',
      actualStart: null,
      actualEnd: null,
      startColumn: startCol,
      endColumn: endCol
    };

    setTasks([...tasks, task]);
    setShowCreateDialog(false);
    setNewTask({
      title: '',
      role: 'Backend',
      expectedStart: '2026-12-24',
      expectedEnd: '2026-12-24',
      assignee: '',
      estimatedHours: 8,
      dependencies: []
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-amber-50 to-orange-50">
      {/* Header */}
      <div className="border-b border-amber-200/30 bg-white/60 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-[1800px] mx-auto px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-light text-stone-800 tracking-tight mb-1">
                Create New Project
              </h1>
              <p className="text-sm text-stone-500">
                Use Ctrl + scroll to zoom • Vertical spacing preserved
              </p>
            </div>
            <div className="flex gap-3">
              <button 
                onClick={() => setShowCreateDialog(true)}
                className="px-4 py-2 bg-white text-stone-700 border border-stone-200 rounded-lg font-medium text-sm hover:bg-stone-50 transition-all flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Task
              </button>
              <button 
                onClick={() => setShowDependencies(!showDependencies)}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  showDependencies 
                    ? 'bg-amber-100 text-amber-800 border border-amber-300' 
                    : 'bg-white text-stone-600 border border-stone-200 hover:bg-stone-50'
                }`}
              >
                <GitBranch className="w-4 h-4 inline mr-2" />
                {showDependencies ? 'Hide' : 'Show'} Dependencies
              </button>
              <div className="flex items-center gap-2 px-3 py-2 bg-white border border-stone-200 rounded-lg">
                <button 
                  onClick={() => setZoom(prev => Math.max(prev - 0.1, 0.5))}
                  className="w-8 h-8 flex items-center justify-center hover:bg-stone-100 rounded text-stone-600 font-bold text-lg"
                >
                  −
                </button>
                <span className="text-sm font-semibold text-stone-700 min-w-[3.5rem] text-center">
                  {Math.round(zoom * 100)}%
                </span>
                <button 
                  onClick={() => setZoom(prev => Math.min(prev + 0.1, 2))}
                  className="w-8 h-8 flex items-center justify-center hover:bg-stone-100 rounded text-stone-600 font-bold text-lg"
                >
                  +
                </button>
              </div>
              <button className="px-6 py-2.5 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-lg font-medium hover:from-amber-700 hover:to-orange-700 transition-all shadow-sm hover:shadow-md">
                SUBMIT PROJECT
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1800px] mx-auto px-8 py-8">
        {/* Stats Cards - Compact */}
        <div className="grid grid-cols-4 gap-3 mb-6">
          <div className="bg-white/70 backdrop-blur-sm border border-orange-100/50 rounded-lg p-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
                <Calendar className="w-4 h-4 text-amber-700" />
              </div>
              <div>
                <div className="text-xl font-semibold text-stone-800">{tasks.length}</div>
                <div className="text-xs text-stone-500">Total Tasks</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm border border-orange-100/50 rounded-lg p-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-4 h-4 text-red-600" />
              </div>
              <div>
                <div className="text-xl font-semibold text-stone-800">
                  {tasks.filter(t => t.status === 'blocked').length}
                </div>
                <div className="text-xs text-stone-500">Blocked</div>
              </div>
            </div>
          </div>

          <div className="bg-white/70 backdrop-blur-sm border border-orange-100/50 rounded-lg p-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Users className="w-4 h-4 text-blue-700" />
              </div>
              <div>
                <div className="text-xl font-semibold text-stone-800">3</div>
                <div className="text-xs text-stone-500">Roles</div>
              </div>
            </div>
          </div>

          <div className="bg-white/70 backdrop-blur-sm border border-orange-100/50 rounded-lg p-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <Clock className="w-4 h-4 text-emerald-700" />
              </div>
              <div>
                <div className="text-xl font-semibold text-stone-800">34h</div>
                <div className="text-xs text-stone-500">Estimated</div>
              </div>
            </div>
          </div>
        </div>

        {/* Timeline Grid with Scroll */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-sm border border-orange-100/50 overflow-auto" style={{ maxHeight: '80vh' }}>
          {/* Column Headers - Sticky */}
          <div className="grid grid-cols-5 border-b-2 border-orange-200/50 bg-gradient-to-r from-amber-100/80 to-orange-100/80 sticky top-0 z-10">
            {days.map((d, i) => (
              <div
                key={i}
                className="p-4 text-center border-r border-orange-200/50 last:border-r-0"
              >
                <div className="text-xs font-bold text-stone-600 uppercase tracking-wider mb-1">
                  {d.day}
                </div>
                <div className="text-2xl font-bold text-stone-800">{d.date}</div>
                <div className="text-xs text-stone-500 font-medium mt-0.5">{d.label}</div>
              </div>
            ))}
          </div>

          {/* Zoom Container */}
          <div 
            style={{ 
              transform: `scale(${zoom})`, 
              transformOrigin: 'top left',
              width: `${100 / zoom}%`,
              height: `${100 / zoom}%`
            }}
          >
            {/* Task Grid */}
            <div className="relative" ref={gridRef} style={{ minHeight: '1000px' }}>
              {/* Grid Background */}
              <div className="absolute inset-0">
                <div className="grid grid-cols-5 h-full">
                  {days.map((d, i) => (
                    <div 
                      key={i} 
                      className="border-r border-orange-100/50 last:border-r-0 bg-gradient-to-b from-transparent via-orange-50/10 to-orange-50/20"
                    />
                  ))}
                </div>
              </div>

              {/* SVG Arrows */}
              {showDependencies && (
                <svg 
                  className="absolute inset-0 pointer-events-none" 
                  style={{ width: '100%', height: '100%', zIndex: 1 }}
                >
                  <defs>
                    <marker
                      id="arrowhead"
                      markerWidth="12"
                      markerHeight="12"
                      refX="10"
                      refY="3.5"
                      orient="auto"
                    >
                      <polygon
                        points="0 0, 12 3.5, 0 7"
                        fill="#F59E0B"
                      />
                    </marker>
                  </defs>
                  {tasks.map(task => {
                    return task.dependencies.map(depId => {
                      const depTask = tasks.find(t => t.id === depId);
                      if (!depTask || !taskRefs.current[task.id] || !taskRefs.current[depId]) return null;

                      const fromEl = taskRefs.current[depId];
                      const toEl = taskRefs.current[task.id];
                      const gridEl = gridRef.current;

                      if (!fromEl || !toEl || !gridEl) return null;

                      const fromRect = fromEl.getBoundingClientRect();
                      const toRect = toEl.getBoundingClientRect();
                      const gridRect = gridEl.getBoundingClientRect();

                      const startX = (fromRect.right - gridRect.left) / zoom;
                      const startY = (fromRect.top + fromRect.height / 2 - gridRect.top) / zoom;
                      const endX = (toRect.left - gridRect.left) / zoom;
                      const endY = (toRect.top + toRect.height / 2 - gridRect.top) / zoom;

                      const midX = (startX + endX) / 2;
                      const curveOffset = Math.abs(endY - startY) * 0.25;

                      return (
                        <g key={`${depId}-${task.id}`}>
                          <path
                            d={`M ${startX} ${startY} Q ${midX} ${startY - curveOffset}, ${midX} ${(startY + endY) / 2} Q ${midX} ${endY + curveOffset}, ${endX - 12} ${endY}`}
                            stroke="#F59E0B"
                            strokeWidth="3"
                            fill="none"
                            markerEnd="url(#arrowhead)"
                            opacity="0.85"
                            strokeDasharray="6,4"
                          />
                          <text
                            x={midX}
                            y={(startY + endY) / 2 - 15}
                            fill="#92400E"
                            fontSize="11"
                            fontWeight="800"
                            textAnchor="middle"
                            className="select-none"
                          >
                            DEPENDS ON
                          </text>
                        </g>
                      );
                    });
                  })}
                </svg>
              )}

              {/* Tasks - Compact Cards */}
              <div className="relative p-4" style={{ zIndex: 2 }}>
                {tasks.map((task) => {
                  const role = roleConfig[task.role];
                  const status = statusConfig[task.status];
                  const span = task.endColumn - task.startColumn + 1;
                  const columnWidth = 100 / 5;
                  const left = `${task.startColumn * columnWidth}%`;
                  const width = `calc(${span * columnWidth}% - 1.5rem)`;
                  const assignedRow = taskRowAssignments[task.id] || 0;
                  const top = `${assignedRow * 240 + 16}px`;
                  
                  return (
                    <div
                      key={task.id}
                      ref={el => {
                        if (el) taskRefs.current[task.id] = el;
                      }}
                      className="absolute"
                      style={{ left, width, top }}
                      onClick={() => setSelectedTask(task)}
                    >
                      {/* Compact Task Card */}
                      <div 
                        className="relative rounded-lg border-2 transition-all cursor-pointer hover:shadow-xl hover:-translate-y-0.5"
                        style={{
                          backgroundColor: '#FFFFFF',
                          borderColor: status.border,
                          boxShadow: selectedTask?.id === task.id ? `0 0 0 3px ${status.border}40` : '0 2px 6px rgba(0,0,0,0.08)'
                        }}
                      >
                        {/* Header with Status Badge */}
                        <div 
                          className="px-3 py-2 rounded-t-md flex items-center justify-between"
                          style={{
                            backgroundColor: status.bg,
                            borderBottom: `2px solid ${status.border}`
                          }}
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{role.icon}</span>
                            <span className="text-xs font-bold text-stone-700">{task.role.toUpperCase()}</span>
                          </div>
                          <span 
                            className="px-2 py-0.5 rounded text-xs font-black tracking-wide"
                            style={{
                              backgroundColor: status.color,
                              color: status.label === 'BLOCKED' ? '#FFFFFF' : status.color === '#FFFFFF' ? '#92400E' : '#FFFFFF'
                            }}
                          >
                            {status.label}
                          </span>
                        </div>

                        {/* Body */}
                        <div className="p-3">
                          {span > 1 && (
                            <div className="mb-2">
                              <span 
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold"
                                style={{
                                  backgroundColor: role.secondary,
                                  color: role.dark
                                }}
                              >
                                <ArrowRight className="w-3 h-3" />
                                {span} DAYS
                              </span>
                            </div>
                          )}
                          
                          <h3 className="font-bold text-stone-900 mb-2 leading-tight text-sm">
                            {task.title}
                          </h3>
                          
                          <div className="space-y-1.5 text-xs">
                            <div className="flex items-center gap-1.5 text-stone-700">
                              <Users className="w-3.5 h-3.5 flex-shrink-0" />
                              <span className="font-semibold truncate">{task.assignee}</span>
                            </div>
                            <div className="flex items-center gap-1.5 text-stone-600">
                              <Clock className="w-3.5 h-3.5 flex-shrink-0" />
                              <span className="font-medium">{task.estimatedHours}h</span>
                            </div>
                            {task.dependencies.length > 0 && (
                              <div 
                                className="flex items-center gap-1.5 font-bold"
                                style={{ color: role.dark }}
                              >
                                <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                                <span>{task.dependencies.length} blocker(s)</span>
                              </div>
                            )}
                          </div>

                          {/* Dates */}
                          <div className="mt-2 pt-2 border-t border-stone-200">
                            <div className="flex items-center justify-between text-xs font-bold text-stone-600">
                              <span>{task.expectedStart}</span>
                              {span > 1 && <span>{task.expectedEnd}</span>}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <span className="font-bold text-stone-600">ROLES:</span>
            {Object.entries(roleConfig).map(([role, config]) => (
              <div key={role} className="flex items-center gap-1.5">
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: config.primary }}
                ></div>
                <span className="font-semibold text-stone-700">{role}</span>
              </div>
            ))}
          </div>
          <span className="text-stone-500 font-medium">Use Ctrl + Scroll to zoom</span>
        </div>

        {/* Create Task Dialog */}
        {showCreateDialog && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-8 z-50" onClick={() => setShowCreateDialog(false)}>
            <div 
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-8 max-h-[85vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-light text-stone-800">Create New Task</h2>
                <button 
                  onClick={() => setShowCreateDialog(false)}
                  className="text-stone-400 hover:text-stone-600 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Task Title *
                  </label>
                  <input
                    type="text"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                    className="w-full px-4 py-2.5 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none transition-all"
                    placeholder="e.g., Implement user authentication"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Role *
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {Object.entries(roleConfig).map(([role, config]) => (
                      <button
                        key={role}
                        onClick={() => setNewTask({ ...newTask, role })}
                        className={`p-3 rounded-lg border-2 transition-all text-left ${
                          newTask.role === role
                            ? 'border-current shadow-md'
                            : 'border-stone-200 hover:border-stone-300'
                        }`}
                        style={{
                          backgroundColor: newTask.role === role ? config.secondary : 'white',
                          color: newTask.role === role ? config.primary : '#57534e'
                        }}
                      >
                        <div className="text-2xl mb-1">{config.icon}</div>
                        <div className="font-medium text-sm">{role}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-stone-700 mb-2">
                      Expected Start Date *
                    </label>
                    <select
                      value={newTask.expectedStart}
                      onChange={(e) => setNewTask({ ...newTask, expectedStart: e.target.value })}
                      className="w-full px-4 py-2.5 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
                    >
                      {days.map(d => (
                        <option key={d.value} value={d.value}>
                          {d.day}, {d.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-stone-700 mb-2">
                      Expected End Date *
                    </label>
                    <select
                      value={newTask.expectedEnd}
                      onChange={(e) => setNewTask({ ...newTask, expectedEnd: e.target.value })}
                      className="w-full px-4 py-2.5 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
                    >
                      {days.map(d => (
                        <option key={d.value} value={d.value}>
                          {d.day}, {d.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Assignee *
                  </label>
                  <input
                    type="text"
                    value={newTask.assignee}
                    onChange={(e) => setNewTask({ ...newTask, assignee: e.target.value })}
                    className="w-full px-4 py-2.5 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
                    placeholder="e.g., John Smith"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Estimated Hours *
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={newTask.estimatedHours}
                    onChange={(e) => setNewTask({ ...newTask, estimatedHours: parseInt(e.target.value) })}
                    className="w-full px-4 py-2.5 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Dependencies (Blockers)
                  </label>
                  <div className="border border-stone-300 rounded-lg p-4 max-h-48 overflow-y-auto space-y-2">
                    {tasks.length === 0 ? (
                      <p className="text-sm text-stone-500">No tasks available yet</p>
                    ) : (
                      tasks.map(task => (
                        <label
                          key={task.id}
                          className="flex items-center gap-3 p-2 hover:bg-stone-50 rounded-lg cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={newTask.dependencies.includes(task.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setNewTask({
                                  ...newTask,
                                  dependencies: [...newTask.dependencies, task.id]
                                });
                              } else {
                                setNewTask({
                                  ...newTask,
                                  dependencies: newTask.dependencies.filter(id => id !== task.id)
                                });
                              }
                            }}
                            className="w-4 h-4 text-amber-600 rounded focus:ring-amber-500"
                          />
                          <div className="flex-1">
                            <div className="text-sm font-medium text-stone-800">{task.title}</div>
                            <div className="text-xs text-stone-500">{task.role} • {task.assignee}</div>
                          </div>
                          <span 
                            className="text-xs px-2 py-1 rounded"
                            style={{
                              backgroundColor: roleConfig[task.role].secondary,
                              color: roleConfig[task.role].primary
                            }}
                          >
                            {task.role}
                          </span>
                        </label>
                      ))
                    )}
                  </div>
                  <p className="text-xs text-stone-500 mt-2">
                    Select tasks that must be completed before this task can start (Finish-to-Start dependency)
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={() => setShowCreateDialog(false)}
                    className="flex-1 px-4 py-2.5 border border-stone-300 text-stone-700 rounded-lg font-medium hover:bg-stone-50 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={createTask}
                    disabled={!newTask.title || !newTask.assignee}
                    className="flex-1 px-4 py-2.5 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-lg font-medium hover:from-amber-700 hover:to-orange-700 transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <Check className="w-4 h-4" />
                    Create Task
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Task Detail Panel */}
        {selectedTask && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-8 z-50" onClick={() => setSelectedTask(null)}>
            <div 
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-8 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <span 
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium"
                      style={{ 
                        backgroundColor: roleConfig[selectedTask.role].secondary,
                        color: roleConfig[selectedTask.role].primary 
                      }}
                    >
                      <span>{roleConfig[selectedTask.role].icon}</span>
                      {selectedTask.role}
                    </span>
                    <span 
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                      style={{
                        backgroundColor: statusConfig[selectedTask.status].bg,
                        color: statusConfig[selectedTask.status].color
                      }}
                    >
                      {statusConfig[selectedTask.status].label}
                    </span>
                  </div>
                  <h2 className="text-2xl font-light text-stone-800">{selectedTask.title}</h2>
                </div>
                <button 
                  onClick={() => setSelectedTask(null)}
                  className="text-stone-400 hover:text-stone-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <div className="text-xs font-medium text-stone-500 uppercase tracking-wider mb-2">
                    Assigned To
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white font-medium">
                      {selectedTask.assignee.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <div className="font-medium text-stone-800">{selectedTask.assignee}</div>
                      <div className="text-xs text-stone-500">{selectedTask.role}</div>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-xs font-medium text-stone-500 uppercase tracking-wider mb-3">
                    Schedule Information
                  </div>
                  <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-stone-600">Expected Start:</span>
                      <span className="font-medium text-stone-800">{selectedTask.expectedStart}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-stone-600">Expected End:</span>
                      <span className="font-medium text-stone-800">{selectedTask.expectedEnd}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-stone-600">Estimated Duration:</span>
                      <span className="font-medium text-stone-800">{selectedTask.estimatedHours}h</span>
                    </div>
                  </div>
                </div>

                {selectedTask.dependencies.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-stone-500 uppercase tracking-wider mb-3">
                      Dependencies (Blockers)
                    </div>
                    <div className="space-y-2">
                      {selectedTask.dependencies.map(depId => {
                        const depTask = tasks.find(t => t.id === depId);
                        return depTask ? (
                          <div 
                            key={depId}
                            className="flex items-center gap-3 p-3 rounded-lg border-2"
                            style={{
                              backgroundColor: roleConfig[depTask.role].secondary,
                              borderColor: roleConfig[depTask.role].primary + '40'
                            }}
                          >
                            <ArrowRight className="w-4 h-4 text-amber-600" />
                            <div className="flex-1">
                              <div className="font-medium text-sm text-stone-800">{depTask.title}</div>
                              <div className="text-xs text-stone-500">{depTask.role} • {depTask.assignee}</div>
                            </div>
                          </div>
                        ) : null;
                      })}
                    </div>
                  </div>
                )}

                {(() => {
                  const dependents = getDependentTasks(selectedTask.id);
                  return dependents.length > 0 && (
                    <div>
                      <div className="text-xs font-medium text-stone-500 uppercase tracking-wider mb-3">
                        Dependent Tasks (Will Be Blocked)
                      </div>
                      <div className="space-y-2">
                        {dependents.map(depTask => (
                          <div 
                            key={depTask.id}
                            className="flex items-center gap-3 p-3 rounded-lg border-2"
                            style={{
                              backgroundColor: roleConfig[depTask.role].secondary,
                              borderColor: roleConfig[depTask.role].primary + '40'
                            }}
                          >
                            <ArrowRight className="w-4 h-4 text-amber-600 transform rotate-180" />
                            <div className="flex-1">
                              <div className="font-medium text-sm text-stone-800">{depTask.title}</div>
                              <div className="text-xs text-stone-500">{depTask.role} • {depTask.assignee}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-xs font-medium text-blue-800 mb-2">📋 Business Rules Applied</div>
                  <ul className="text-xs text-blue-700 space-y-1">
                    <li>• BR-022: Expected dates are mutable, actual dates immutable once set</li>
                    <li>• BR-023: Delays detected when actual_end {'>'} expected_end</li>
                    <li>• BR-024: Delays propagate through finish-to-start dependencies</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
