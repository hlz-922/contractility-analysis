def update_cycle_no(i:int, t_start:float, t_end:float):
  '''
  This function updates the contraction cycle number.
  For each cycle, the start and end times were manually labelled.

  Parameters:
  - i: contraction cycle number
  - t_start: the start time of the cycle
  - t_end: the end time of the cycle
  '''
  df['Cycle'] = 0
  time_mask = (df['Time (s)'] >= t_start) & (df['Time (s)'] <= t_end)
  df.loc[time_mask, 'Cycle'] = i

def update_start_time(i):
  '''
  This function updates the start time of each cycle to 0

  Parameters:
  - i: cycle number under study
  '''
  df_cycle = df[df['Cycle'] == i]
  t_start = float(df_cycle.head(1)['Time (s)'])
  df.loc[df['Cycle'] == i, 'Start time (s)'] = t_start

def update_baseline_spontaneous_beating(i:int):
  '''
  This function calculates the baseline (zero strain) of each cycle
  for strain under spontaneous beating

  Parameters:
  - i : cycle number under study
  '''
  df_cycle = df[df['Cycle'] == i]
  width_baseline = df_cycle.tail(15)['RRWidth'].mean()
  length_baseline = df_cycle.tail(15)['RRLength'].mean()
  df.loc[df['Cycle'] == i, 'width_baseline'] = width_baseline
  df.loc[df['Cycle'] == i, 'length_baseline'] = length_baseline

def update_baseline_electrical_pacing(i:int):
  '''
  This function calculates the baseline (zero strain) of each cycle 
  for strain under electrical pacing.
  For each cycle, the minimum five values of width and the maximum five values 
  of length were used as baselines.
  
  Parameters:
  - i : cycle number under study
  '''
  df_cycle = df[df['Cycle'] == i]
  width_array = np.array(df_cycle['RRWidth'])
  width_array.sort() 
  length_array = np.array(df_cycle['RRLength'])
  length_array.sort()
  width_baseline = np.mean(width_array[0:4])
  length_baseline = np.mean(length_array[-5:])
  df.loc[df['Cycle'] == i, 'width_baseline'] = width_baseline
  df.loc[df['Cycle'] == i, 'length_baseline'] = length_baseline

def average_cycle(strain_type:str, start_cycle:int, end_cycle:int):
  '''
  This function plots the average trend for several cycles.
  
  Parameters:
  - strain_type: the strain type under study, can either be width or length
  - start_cycle: the cycle number of the start cycle
  - end_cycle: the cycle number of the end cycle
  
  Return:
  - ave_trend: the average trend for the cycles under study
  - std: the standard deviation for the cycles under study
  '''
  datasets = []
  for i in range(start_cycle, end_cycle):
      df_cycle = df[df['Cycle'] == i]
      x_values = np.array(df_cycle['Calibrate time (s)'])
      y_values = np.array(df_cycle[strain_type])
      dataset = {'x': x_values, 'y': y_values}
      datasets.append(dataset)
  common_x = np.arange(
      max(min(data['x']) for data in datasets),
      min(max(data['x']) for data in datasets) + 0.02,
      0.02)
  interpolated_datasets = []
  for data in datasets:
      y_interp = np.interp(common_x, data['x'], data['y'])
      interpolated_datasets.append(y_interp)
  ave_trend = np.mean(interpolated_datasets, axis=0)
  std = np.std(interpolated_datasets, axis=0)
  return ave_trend, std

def strain_rate_plot(x:list, L: list, W:list):
  '''
  This function plots the strain rate based on the average trend of strain within one cycle

  Parameters:
  - x: calibrated time for one cycle
  - L: length of the construct
  - W: width of the construct
  '''
  This function plots the strain rate 
  dL_dx_M1 = np.diff(L) / np.diff(x)
  dW_dx_M1 = np.diff(W) / np.diff(x)
  # Downsample the data by averaging adjacent points
  window_size = 5
  dL_dx_smoothed = np.convolve(dL_dx_M1, np.ones(window_size) / window_size, mode='same')
  dW_dx_smoothed = np.convolve(dW_dx_M1, np.ones(window_size) / window_size, mode='same')
  x_smoothed = x[:-1]
  plt.plot(x_smoothed, dL_dx_smoothed, 'r', lw=2)
  plt.plot(x_smoothed, dW_dx_smoothed, 'b', lw=2)   
  plt.xlabel('Time within cycle (s)')
  plt.ylabel('Strain rate ($s^{-1}$)') 
  plt.xticks([0,1]) 
  plt.show()
