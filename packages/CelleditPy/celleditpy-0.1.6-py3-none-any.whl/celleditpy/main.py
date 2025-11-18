#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CelleditPy - A GUI tool to set and adjust unit cell parameters for molecular structures.

Author: Hiromichi Yokoyama
License: Apache-2.0 license
Repo: https://github.com/HiroYokoyama/crystal-cell-setter
DOI 10.5281/zenodo.17620125
"""

VERSION = "0.1.6"

import sys
import numpy as np
import pyvista as pv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QGridLayout, QDoubleSpinBox,
    QMessageBox, QSizePolicy, QInputDialog
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from pyvistaqt import QtInteractor
import ase
import ase.io
from ase.geometry import cell_to_cellpar, cellpar_to_cell
from ase.data import vdw_radii, atomic_numbers, covalent_radii
from ase.neighborlist import NeighborList, natural_cutoffs
from scipy.spatial.transform import Rotation

CPK_COLORS = {
    'H': QColor('#FFFFFF'), 'C': QColor('#222222'), 'N': QColor('#3377FF'), 'O': QColor('#FF3333'), 'F': QColor('#99E6E6'),
    'Cl': QColor('#33FF33'), 'Br': QColor('#A52A2A'), 'I': QColor('#9400D3'), 'S': QColor('#FFC000'), 'P': QColor('#FF8000'),
    'Si': QColor('#DAA520'), 'B': QColor('#FA8072'), 'He': QColor('#D9FFFF'), 'Ne': QColor('#B3E3F5'), 'Ar': QColor('#80D1E3'),
    'Kr': QColor('#5CACC8'), 'Xe': QColor('#429EB0'), 'Rn': QColor('#298FA2'), 'Li': QColor('#CC80FF'), 'Na': QColor('#AB5CF2'),
    'K': QColor('#8F44D7'), 'Rb': QColor('#702EBC'), 'Cs': QColor('#561B9E'), 'Fr': QColor('#421384'), 'Be': QColor('#C2FF00'),
    'Mg': QColor('#8AFF00'), 'Ca': QColor('#3DFF00'), 'Sr': QColor('#00FF00'), 'Ba': QColor('#00E600'), 'Ra': QColor('#00B800'),
    'Sc': QColor('#E6E6E6'), 'Ti': QColor('#BFC2C7'), 'V': QColor('#A6A6AB'), 'Cr': QColor('#8A99C7'), 'Mn': QColor('#9C7AC7'),
    'Fe': QColor('#E06633'), 'Co': QColor('#F090A0'), 'Ni': QColor('#50D050'), 'Cu': QColor('#C88033'), 'Zn': QColor('#7D80B0'),
    'Ga': QColor('#C28F8F'), 'Ge': QColor('#668F8F'), 'As': QColor('#BD80E3'), 'Se': QColor('#FFA100'), 'Tc': QColor('#3B9E9E'),
    'Ru': QColor('#248F8F'), 'Rh': QColor('#0A7D8F'), 'Pd': QColor('#006985'), 'Ag': QColor('#C0C0C0'), 'Cd': QColor('#FFD700'),
    'In': QColor('#A67573'), 'Sn': QColor('#668080'), 'Sb': QColor('#9E63B5'), 'Te': QColor('#D47A00'), 'La': QColor('#70D4FF'),
    'Ce': QColor('#FFFFC7'), 'Pr': QColor('#D9FFC7'), 'Nd': QColor('#C7FFC7'), 'Pm': QColor('#A3FFC7'), 'Sm': QColor('#8FFFC7'),
    'Eu': QColor('#61FFC7'), 'Gd': QColor('#45FFC7'), 'Tb': QColor('#30FFC7'), 'Dy': QColor('#1FFFC7'), 'Ho': QColor('#00FF9C'),
    'Er': QColor('#00E675'), 'Tm': QColor('#00D452'), 'Yb': QColor('#00BF38'), 'Lu': QColor('#00AB24'), 'Hf': QColor('#4DC2FF'),
    'Ta': QColor('#4DA6FF'), 'W': QColor('#2194D6'), 'Re': QColor('#267DAB'), 'Os': QColor('#266696'), 'Ir': QColor('#175487'),
    'Pt': QColor('#D0D0E0'), 'Au': QColor('#FFD123'), 'Hg': QColor('#B8B8D0'), 'Tl': QColor('#A6544D'), 'Pb': QColor('#575961'),
    'Bi': QColor('#9E4FB5'), 'Po': QColor('#AB5C00'), 'At': QColor('#754F45'), 'Ac': QColor('#70ABFA'), 'Th': QColor('#00BAFF'),
    'Pa': QColor('#00A1FF'), 'U': QColor('#008FFF'), 'Np': QColor('#0080FF'), 'Pu': QColor('#006BFF'), 'Am': QColor('#545CF2'),
    'Cm': QColor('#785CE3'), 'Bk': QColor('#8A4FE3'), 'Cf': QColor('#A136D4'), 'Es': QColor('#B31FD4'), 'Fm': QColor('#B31FBA'),
    'Md': QColor('#B30DA6'), 'No': QColor('#BD0D87'), 'Lr': QColor('#C70066'), 'Al': QColor('#B3A68F'), 'Y': QColor('#99FFFF'), 
    'Zr': QColor('#7EE7E7'), 'Nb': QColor('#68CFCE'), 'Mo': QColor('#52B7B7'), 'DEFAULT': QColor('#FF1493') # Pink fallback
}


class CellSetterApp(QMainWindow):
    def update_supercell_display(self):
        """スーパーセル表示のON/OFFやパラメータ変更時に呼ばれる。"""
        if self.atoms is None:
            return
        show_supercell = self.supercell_checkbox.isChecked()
        n_a = int(self.supercell_spinboxes['a'].value())
        n_b = int(self.supercell_spinboxes['b'].value())
        n_c = int(self.supercell_spinboxes['c'].value())
        self._supercell_params = (show_supercell, n_a, n_b, n_c)
        # Show SupercellのON/OFFにかかわらず、UIの状態に従って再描画
        cell_center = np.array([0.0, 0.0, 0.0])
        self.draw_scene_manually(force_reset=False, cell_center=cell_center, draw_supercell=show_supercell)

    '''
    def update_supercell_display(self):
        """スーパーセル表示のON/OFFやパラメータ変更時に呼ばれる。描画処理は後で実装。"""
        # ここでsupercell_checkboxの状態とspinbox値を取得し、描画を切り替える処理を追加予定
        # 例:
        # show_supercell = self.supercell_checkbox.isChecked()
        # n_a = int(self.supercell_spinboxes['a'].value())
        # n_b = int(self.supercell_spinboxes['b'].value())
        # n_c = int(self.supercell_spinboxes['c'].value())
        pass
    '''

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"CelleditPy ver. {VERSION}")
        self.setGeometry(100, 100, 1200, 800)

        # --- 内部データ ---
        self.atoms = None
        self.camera_state = None
        self.show_atom_indices = True  # 原子インデックス表示フラグ（デフォルトで表示） 

        # --- メインウィジェットとレイアウト ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- 1. 左側：コントロールパネル ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setMaximumWidth(350)
        control_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # --- Tabs for control sections ---
        from PyQt6.QtWidgets import QTabWidget
        self.control_tabs = QTabWidget()
        # Make sure tabs pack widgets from the top; give the tabs a smaller spacing
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        control_layout.setSpacing(6)

        # Main tab (basic controls)
        self.main_tab = QWidget()
        self.main_tab_layout = QVBoxLayout(self.main_tab)
        self.main_tab_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_tab_layout.setSpacing(6)
        self.control_tabs.addTab(self.main_tab, "Main")

        # Group Control tab (structure/group level operations)
        self.group_tab = QWidget()
        self.group_tab_layout = QVBoxLayout(self.group_tab)
        self.group_tab_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.group_tab_layout.setSpacing(6)
        self.control_tabs.addTab(self.group_tab, "Group Control")

        # Advanced tab (advanced transforms / optimization)
        self.advanced_tab = QWidget()
        self.advanced_tab_layout = QVBoxLayout(self.advanced_tab)
        self.advanced_tab_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.advanced_tab_layout.setSpacing(6)
        self.control_tabs.addTab(self.advanced_tab, "Advanced")

        # === File Operations ===
        file_label = QLabel("=== File Operations ===")
        # File Operations -> Main tab
        self.main_tab_layout.addWidget(file_label)
        
        self.load_button = QPushButton("Load File (.mol, .cif)")
        self.load_button.clicked.connect(self.load_mol_file)
        self.main_tab_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save as CIF")
        self.save_button.clicked.connect(self.save_cif_file)
        self.save_button.setEnabled(False) 
        self.main_tab_layout.addWidget(self.save_button)

        self.main_tab_layout.addSpacing(20)

        # === Cell Parameters ===
        cell_label = QLabel("=== Cell Parameters ===")
        # Cell parameters -> Main tab
        self.main_tab_layout.addWidget(cell_label)
        
        # セルパラメータ入力
        cell_group = QWidget()
        grid_layout = QGridLayout(cell_group)
        
        self.param_inputs = {}

        params_info = {
            'a': (10.0, 1.0, 1000.0, 0.1), 'alpha': (90.0, 0.0, 180.0, 1.0), 
            'b': (10.0, 1.0, 1000.0, 0.1), 'beta':  (90.0, 0.0, 180.0, 1.0),
            'c': (10.0, 1.0, 1000.0, 0.1), 'gamma': (90.0, 0.0, 180.0, 1.0),
        }

        row = 0
        col = 0
        for name, (default, min_val, max_val, step) in params_info.items():
            label = QLabel(f"{name}:")
            spinbox = QDoubleSpinBox()
            spinbox.setValue(default)
            spinbox.setMinimum(min_val)
            spinbox.setMaximum(max_val)
            spinbox.setSingleStep(step)
            spinbox.setDecimals(3) 
            
            grid_layout.addWidget(label, row, col * 2)
            grid_layout.addWidget(spinbox, row, col * 2 + 1)
            
            self.param_inputs[name] = spinbox
            
            col += 1
            if col > 1:
                col = 0
                row += 1

        self.main_tab_layout.addWidget(cell_group)

        self.apply_cell_button = QPushButton("Apply Cell Parameters")
        self.apply_cell_button.clicked.connect(lambda: self.update_cell_and_draw(force_reset=False))
        self.apply_cell_button.setEnabled(False) 
        self.main_tab_layout.addWidget(self.apply_cell_button)

        self.optimize_button = QPushButton("Auto-fit Cell Size")
        self.optimize_button.clicked.connect(self.optimize_cell_size)
        self.optimize_button.setEnabled(False) 
        # Auto-fit: place under Cell in Main tab
        self.main_tab_layout.addWidget(self.optimize_button)

        # === Supercell Parameters ===
        supercell_label = QLabel("=== Supercell ===")
        # Supercell -> Main tab
        self.main_tab_layout.addWidget(supercell_label)

        supercell_group = QWidget()
        supercell_layout = QGridLayout(supercell_group)

        self.supercell_spinboxes = {}
        axes = ['a', 'b', 'c']
        for i, axis in enumerate(axes):
            label = QLabel(f"n_{axis}:")
            spinbox = QDoubleSpinBox()
            spinbox.setDecimals(0)
            spinbox.setMinimum(1)
            spinbox.setMaximum(10)
            spinbox.setValue(1)
            supercell_layout.addWidget(label, 0, i * 2)
            supercell_layout.addWidget(spinbox, 0, i * 2 + 1)
            self.supercell_spinboxes[axis] = spinbox

        from PyQt6.QtWidgets import QCheckBox
        self.supercell_checkbox = QCheckBox("Show Supercell")
        self.supercell_checkbox.setChecked(False)
        supercell_layout.addWidget(self.supercell_checkbox, 1, 0, 1, 6)

        self.main_tab_layout.addWidget(supercell_group)

        # Connect signals for supercell controls
        self.supercell_checkbox.stateChanged.connect(self.update_supercell_display)
        for spinbox in self.supercell_spinboxes.values():
            spinbox.valueChanged.connect(self.update_supercell_display)
        
        self.main_tab_layout.addSpacing(20)
        
        # === Structure Operations ===
        struct_label = QLabel("=== Structure Operations ===")
        # Structure operations -> Main tab (option 3)
        self.main_tab_layout.addWidget(struct_label)
        
        self.fit_to_cell_button = QPushButton("Fit Molecule to Axis")
        self.fit_to_cell_button.clicked.connect(self.fit_molecule_to_cell)
        self.fit_to_cell_button.setEnabled(False)
        self.main_tab_layout.addWidget(self.fit_to_cell_button)
        
        self.fix_atom0_button = QPushButton("Fit in Cell")
        self.fix_atom0_button.clicked.connect(self.fix_atom0_and_fit)
        self.fix_atom0_button.setEnabled(False)
        self.main_tab_layout.addWidget(self.fix_atom0_button)
        
        self.optimize_coord_button = QPushButton("Wrap into Cell")
        self.optimize_coord_button.clicked.connect(self.optimize_coordinate)
        self.optimize_coord_button.setEnabled(False) 
        self.main_tab_layout.addWidget(self.optimize_coord_button)

        # --- 原子削除ボタン ---
        self.delete_atom_button = QPushButton("Delete Atom(s)")
        self.delete_atom_button.clicked.connect(self.delete_atoms_dialog)
        self.delete_atom_button.setEnabled(False)
        self.main_tab_layout.addWidget(self.delete_atom_button)
        
        self.main_tab_layout.addSpacing(20)
        
        # === Transform Controls ===
        transform_label = QLabel("=== Transform Controls ===")
        # Transform Controls -> Group Control tab (option 3)
        self.group_tab_layout.addWidget(transform_label)
        
        # 平行移動 (XYZ / ABCモード切り替え)
        translate_group = QWidget()
        translate_layout = QGridLayout(translate_group)
        translate_layout.addWidget(QLabel("Translation (Å):"), 0, 0, 1, 2)
        
        # モード切り替えボタン
        from PyQt6.QtWidgets import QButtonGroup, QRadioButton
        self.translate_mode_group = QButtonGroup(translate_group)
        self.translate_xyz_radio = QRadioButton("XYZ mode")
        self.translate_abc_radio = QRadioButton("ABC mode")
        self.translate_xyz_radio.setChecked(True)
        self.translate_mode_group.addButton(self.translate_xyz_radio)
        self.translate_mode_group.addButton(self.translate_abc_radio)
        
        translate_layout.addWidget(self.translate_xyz_radio, 1, 0)
        translate_layout.addWidget(self.translate_abc_radio, 1, 1)
        
        # 軸入力（共通ラベルとスピンボックス）
        self.translate_labels = []
        self.translate_spinboxes = []
        self.translate_inputs = {}
        self.translate_abc_inputs = {}
        
        for i in range(3):
            label = QLabel()
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-1000.0, 1000.0)
            spinbox.setValue(0.0)
            spinbox.setSingleStep(0.1)
            spinbox.setDecimals(3)
            translate_layout.addWidget(label, i + 2, 0)
            translate_layout.addWidget(spinbox, i + 2, 1)
            self.translate_labels.append(label)
            self.translate_spinboxes.append(spinbox)
        
        # XYZ/ABCの参照を設定
        for i, axis in enumerate(['X', 'Y', 'Z']):
            self.translate_inputs[axis] = self.translate_spinboxes[i]
        for i, axis in enumerate(['a', 'b', 'c']):
            self.translate_abc_inputs[axis] = self.translate_spinboxes[i]
        
        # 初期状態をXYZに設定
        for i, axis in enumerate(['X', 'Y', 'Z']):
            self.translate_labels[i].setText(f"{axis}:")
        
        # モード切り替え時の処理
        def update_translate_labels():
            is_xyz = self.translate_xyz_radio.isChecked()
            if is_xyz:
                # XYZモード
                for i, axis in enumerate(['X', 'Y', 'Z']):
                    self.translate_labels[i].setText(f"{axis}:")
            else:
                # ABCモード
                for i, axis in enumerate(['a', 'b', 'c']):
                    self.translate_labels[i].setText(f"{axis}:")
        
        self.translate_xyz_radio.toggled.connect(update_translate_labels)
        
        apply_translate_button = QPushButton("Apply Translation")
        apply_translate_button.clicked.connect(self.apply_translation)
        translate_layout.addWidget(apply_translate_button, 5, 0, 1, 2)
        self.group_tab_layout.addWidget(translate_group)
        
        # 回転 (XYZ / ABC モード切り替え)
        rotate_group = QWidget()
        rotate_layout = QGridLayout(rotate_group)
        rotate_layout.addWidget(QLabel("Rotation (degrees):"), 0, 0, 1, 2)
        
        # モード切り替えボタン
        self.rotate_mode_group = QButtonGroup(rotate_group)
        self.rotate_xyz_radio = QRadioButton("XYZ mode")
        self.rotate_abc_radio = QRadioButton("ABC mode")
        self.rotate_xyz_radio.setChecked(True)
        self.rotate_mode_group.addButton(self.rotate_xyz_radio)
        self.rotate_mode_group.addButton(self.rotate_abc_radio)
        
        rotate_layout.addWidget(self.rotate_xyz_radio, 1, 0)
        rotate_layout.addWidget(self.rotate_abc_radio, 1, 1)
        
        # 軸入力（共通ラベルとスピンボックス）
        self.rotate_labels = []
        self.rotate_spinboxes = []
        self.rotate_inputs = {}
        self.rotate_abc_inputs = {}
        
        for i in range(3):
            label = QLabel()
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-360.0, 360.0)
            spinbox.setValue(0.0)
            spinbox.setSingleStep(1.0)
            spinbox.setDecimals(2)
            rotate_layout.addWidget(label, i + 2, 0)
            rotate_layout.addWidget(spinbox, i + 2, 1)
            self.rotate_labels.append(label)
            self.rotate_spinboxes.append(spinbox)
        
        # XYZ/ABCの参照を設定
        for i, axis in enumerate(['X', 'Y', 'Z']):
            self.rotate_inputs[axis] = self.rotate_spinboxes[i]
        for i, axis in enumerate(['a', 'b', 'c']):
            self.rotate_abc_inputs[axis] = self.rotate_spinboxes[i]
        
        # 初期状態をXYZに設定
        for i, axis in enumerate(['X', 'Y', 'Z']):
            self.rotate_labels[i].setText(f"Around {axis}:")
        
        # モード切り替え時の処理
        def update_rotate_labels():
            is_xyz = self.rotate_xyz_radio.isChecked()
            if is_xyz:
                # XYZモード
                for i, axis in enumerate(['X', 'Y', 'Z']):
                    self.rotate_labels[i].setText(f"Around {axis}:")
            else:
                # ABCモード
                for i, axis in enumerate(['a', 'b', 'c']):
                    self.rotate_labels[i].setText(f"Around {axis}:")
        
        self.rotate_xyz_radio.toggled.connect(update_rotate_labels)
        
        apply_rotate_button = QPushButton("Apply Rotation")
        apply_rotate_button.clicked.connect(self.apply_rotation)
        rotate_layout.addWidget(apply_rotate_button, 5, 0, 1, 2)
        self.group_tab_layout.addWidget(rotate_group)
        
        self.advanced_tab_layout.addSpacing(20)
        
        # === View Controls ===
        view_label = QLabel("=== View Controls ===")
        # View controls -> Advanced tab (option 3)
        self.advanced_tab_layout.addWidget(view_label)

        self.toggle_indices_button = QPushButton("Toggle Atom Indices")
        self.toggle_indices_button.clicked.connect(self.toggle_atom_indices)
        self.toggle_indices_button.setEnabled(False)
        self.advanced_tab_layout.addWidget(self.toggle_indices_button)

        self.reset_camera_button = QPushButton("Reset Camera")
        self.reset_camera_button.clicked.connect(self.reset_camera_view)
        self.reset_camera_button.setEnabled(False) 
        self.advanced_tab_layout.addWidget(self.reset_camera_button)

        # Add tab widget to control_panel instead of the flat control layout
        control_layout.addWidget(self.control_tabs)
        main_layout.addWidget(control_panel)

        # --- 2. 右側：3Dビュー (PyVista) ---
        self.plotter = QtInteractor(main_widget)
        self.plotter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.plotter)
        
        self.plotter.set_background('#919191')
        self.plotter.add_axes()

    def _set_spinbox_values(self, params_dict):
        """セルパラメータ辞書からSpinBoxの値を設定する"""
        for name, spinbox in self.param_inputs.items():
            spinbox.blockSignals(True)
            if name in params_dict:
                value = params_dict[name]
                value = max(spinbox.minimum(), min(spinbox.maximum(), value))
                spinbox.setValue(value)
            spinbox.blockSignals(False)

    def load_mol_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Structure File",
            "",
            "Structure Files (*.mol *.cif);;All Files (*.*)"
        )
        if file_name:
            try:
                self.atoms = ase.io.read(file_name)
                
                cell_params = self.atoms.cell.cellpar()
                
                if np.any(cell_params) and not np.all(cell_params[:3] == 0):
                    params_dict = {
                        'a': cell_params[0], 'b': cell_params[1], 'c': cell_params[2],
                        'alpha': cell_params[3], 'beta': cell_params[4], 'gamma': cell_params[5]
                    }
                    self._set_spinbox_values(params_dict)
                    self.atoms.set_pbc(True)
                else:
                    # MOLファイルの場合
                    # Auto-fit cell sizeでセルを作成
                    self.optimize_cell_size()
                    # 分子をセルの中心に配置
                    cell = self.atoms.get_cell()
                    cell_center = (cell[0] + cell[1] + cell[2]) / 2.0
                    mol_center = self.atoms.get_center_of_mass()
                    self.atoms.positions += (cell_center - mol_center)
                    # 再描画
                    self.draw_scene_manually(force_reset=False, cell_center=np.array([0.0, 0.0, 0.0])) 

                self.save_button.setEnabled(True)
                self.optimize_button.setEnabled(True) 
                self.reset_camera_button.setEnabled(True) 
                self.apply_cell_button.setEnabled(True) 
                self.optimize_coord_button.setEnabled(True) 
                self.fit_to_cell_button.setEnabled(True) # [追加 v18]
                self.toggle_indices_button.setEnabled(True) # [追加 v19]
                self.fix_atom0_button.setEnabled(True) # [追加 v22]
                self.delete_atom_button.setEnabled(True)
                
                # [追加 v20] Transform controls
                for spinbox in self.translate_spinboxes:
                    spinbox.setEnabled(True)
                for spinbox in self.rotate_spinboxes:
                    spinbox.setEnabled(True)

                if not (file_name.endswith('.mol') or file_name.endswith('.MOL')):
                     self.update_cell_and_draw(force_reset=True)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")
                self.atoms = None
                self.save_button.setEnabled(False)
                self.optimize_button.setEnabled(False) 
                self.reset_camera_button.setEnabled(False) 
                self.apply_cell_button.setEnabled(False) 
                self.optimize_coord_button.setEnabled(False) 
                self.fit_to_cell_button.setEnabled(False) # [追加 v18]
                self.toggle_indices_button.setEnabled(False) # [追加 v19]
                self.fix_atom0_button.setEnabled(False) # [追加 v22]
                self.delete_atom_button.setEnabled(False)
    
                # [追加 v20] Transform controls
                for spinbox in self.translate_spinboxes:
                    spinbox.setEnabled(False)
                for spinbox in self.rotate_spinboxes:
                    spinbox.setEnabled(False)

    def delete_atoms_dialog(self):
        """原子インデックスを入力して削除するダイアログ"""
        if self.atoms is None:
            return
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        text, ok = QInputDialog.getText(self, "Delete Atom(s)", f"Enter atom index or indices (comma-separated, 0-{len(self.atoms)-1}):", text="0")
        if not ok or not text.strip():
            return
        try:
            indices = []
            for part in text.split(','):
                idx = int(part.strip())
                if idx < 0 or idx >= len(self.atoms):
                    raise ValueError(f"Index {idx} out of range.")
                indices.append(idx)
            indices = sorted(set(indices), reverse=True)  # 大きい順で削除
            if not indices:
                raise ValueError("No valid indices specified.")
            self.delete_atoms(indices)
        except Exception as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {e}")     
    
    def delete_atoms(self, indices):
        """指定したインデックスの原子を削除し、再描画"""
        from PyQt6.QtWidgets import QMessageBox
        try:
            # ASEのAtomsオブジェクトから原子を削除
            mask = np.ones(len(self.atoms), dtype=bool)
            for idx in indices:
                mask[idx] = False
            self.atoms = self.atoms[mask]
            # 再描画
            cell_center = np.array([0.0, 0.0, 0.0])
            self.draw_scene_manually(force_reset=False, cell_center=cell_center)
            QMessageBox.information(self, "Success", f"Deleted atom(s): {', '.join(map(str, indices))}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete atom(s):\n{e}")
                

    # --- Auto-fit Cell Size: 現在の角度を保持してサイズのみ調整 ---
    def optimize_cell_size(self):
        """現在のセル角度を保持し、分子が収まるようにa, b, cサイズのみを調整"""
        if self.atoms is None:
            return

        try:
            # 現在のセルパラメータを取得
            current_cell = self.atoms.get_cell()
            current_params = self.atoms.cell.cellpar()
            
            # セルが設定されていない場合（MOL読み込み直後など）はXYZ基準で直交セルを作成
            if np.all(current_params[:3] == 0) or not np.any(current_params):
                alpha, beta, gamma = 90.0, 90.0, 90.0
                cell_directions = [
                    np.array([1.0, 0.0, 0.0]),
                    np.array([0.0, 1.0, 0.0]),
                    np.array([0.0, 0.0, 1.0])
                ]
            else:
                # 現在の角度を保持
                alpha = current_params[3]
                beta = current_params[4]
                gamma = current_params[5]
                
                # セル軸方向のベクトルを正規化
                cell_directions = []
                for i in range(3):
                    direction = current_cell[i] / np.linalg.norm(current_cell[i])
                    cell_directions.append(direction)
            
            # 現在の原子位置を取得
            positions = self.atoms.get_positions()
            
            # VdW半径を取得
            try:
                atomic_nums = self.atoms.get_atomic_numbers()
                vdw_max_index = len(vdw_radii)
                radii = np.array([
                    vdw_radii[num] if (num < vdw_max_index and vdw_radii[num] > 0) else 1.5
                    for num in atomic_nums
                ])
            except Exception as e:
                print(f"Could not get VdW radii, using default 1.5Å. Error: {e}")
                radii = np.full(positions.shape[0], 1.5)
            
            # ABC軸それぞれの方向に対して必要な長さを計算
            new_sizes = []
            for i, direction in enumerate(cell_directions):
                # 各原子をこのセル軸方向に投影
                coords_along_axis = np.dot(positions, direction)
                
                # この軸方向の最小・最大位置にある原子を特定
                min_idx = np.argmin(coords_along_axis)
                max_idx = np.argmax(coords_along_axis)
                
                # その原子のVdW半径を取得（直径ではなく半径）
                min_atom_vdw = radii[min_idx]
                max_atom_vdw = radii[max_idx]
                
                # 軸方向の座標範囲
                min_coord_axis = coords_along_axis[min_idx]
                max_coord_axis = coords_along_axis[max_idx]
                
                # 分子の範囲（末端原子の中心間距離）
                molecule_span = max_coord_axis - min_coord_axis
                
                # 末端側にのみVdW半径を加算（最大側に加算）
                required_size = molecule_span + max_atom_vdw
                
                # nan/infチェックと範囲制限
                if not np.isfinite(required_size):
                    raise ValueError(f"Invalid size detected for axis {i}")
                
                required_size = max(min(required_size, 1000.0), 1.0)
                new_sizes.append(required_size)
            
            # 新しいセルパラメータを設定
            params_dict = {
                'a': new_sizes[0],
                'b': new_sizes[1],
                'c': new_sizes[2],
                'alpha': alpha,
                'beta': beta,
                'gamma': gamma
            }
            
            self._set_spinbox_values(params_dict)
            
            # セルを適用（分子の位置は変更しない）
            new_cell_matrix = cellpar_to_cell([
                params_dict['a'], params_dict['b'], params_dict['c'],
                params_dict['alpha'], params_dict['beta'], params_dict['gamma']
            ])
            
            self.atoms.set_cell(new_cell_matrix, scale_atoms=False)
            self.atoms.set_pbc(True)
            
            # カメラをリセットして再描画
            self.update_cell_and_draw(force_reset=True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during cell size optimization:\n{e}")
    # --- ここまで ---
    
    # --- [変更なし v14] update_cell_and_draw (重心をセルの中心に) ---
    def update_cell_and_draw(self, force_reset=False):
        if self.atoms is None:
            return
            
        try:
            params = {name: spinbox.value() for name, spinbox in self.param_inputs.items()}
            
            cell_matrix = cellpar_to_cell([
                params['a'], params['b'], params['c'],
                params['alpha'], params['beta'], params['gamma']
            ])
            
            self.atoms.set_cell(cell_matrix)
            self.atoms.set_pbc(True) 
            
            # セルの中心を原点として使用
            cell_center = np.array([0.0, 0.0, 0.0])
            self.draw_scene_manually(force_reset=force_reset, cell_center=cell_center)

        except Exception as e:
            print(f"Cell parameter error: {e}")

    # --- [変更なし v14] draw_scene_manually (カメラの焦点を cell_center に設定) ---

    def draw_scene_manually(self, force_reset=False, cell_center=(0.0, 0.0, 0.0), draw_supercell=None):
        if self.atoms is None:
            return

        # スーパーセル表示のためのatoms拡張
        # draw_supercell が None の場合は UI の現在の状態を参照
        show_supercell = draw_supercell if draw_supercell is not None else getattr(self, '_supercell_params', (False, 1, 1, 1))[0]
        n_a = getattr(self, '_supercell_params', (False, 1, 1, 1))[1]
        n_b = getattr(self, '_supercell_params', (False, 1, 1, 1))[2]
        n_c = getattr(self, '_supercell_params', (False, 1, 1, 1))[3]

        if show_supercell and (n_a > 1 or n_b > 1 or n_c > 1):
            try:
                from ase.build import make_supercell
                P = np.diag([n_a, n_b, n_c])
                atoms_to_draw = make_supercell(self.atoms, P)
            except Exception as e:
                print(f"Supercell error: {e}")
                atoms_to_draw = self.atoms
        else:
            # 非スーパーセル表示ではセル内だけを描画するため、セル内にfoldしたコピーを使う
            try:
                atoms_to_draw = self.atoms.copy()
                # wrap が PBC を前提とするため、万一 PBC が設定されていない場合は wrap を行わない
                if atoms_to_draw.pbc.any():
                    atoms_to_draw.wrap(pbc=atoms_to_draw.pbc)
            except Exception:
                # 何らかの問題があれば元の atoms を描画
                atoms_to_draw = self.atoms

        if not force_reset and self.plotter.camera:
            self.camera_state = self.plotter.camera.copy()

        self.plotter.clear()
        self.plotter.set_background('#919191')

        light = pv.Light(
            position=(5, 5, 15), 
            light_type='cameralight', 
            intensity=1.0
        )
        self.plotter.add_light(light)
        
        mesh_props = dict(
            smooth_shading=True,
            specular=0.2,
            specular_power=20,
            lighting=True,
        )

        symbols = atoms_to_draw.get_chemical_symbols()
        positions = atoms_to_draw.get_positions()

        # --- 1. 原子を描画 (Glyph B) ---
        atom_colors_list = [] 
        atom_radii_list = []
        
        vdw_max_index = len(vdw_radii)

        if len(positions) > 0:
            for symbol in symbols:
                try:
                    color_qcolor = CPK_COLORS.get(symbol, CPK_COLORS['DEFAULT'])
                    color_rgb = (color_qcolor.redF(), color_qcolor.greenF(), color_qcolor.blueF())
                    atom_colors_list.append(color_rgb)
                    atom_num = atomic_numbers[symbol] 
                    if atom_num < vdw_max_index and vdw_radii[atom_num] > 0:
                        radius = vdw_radii[atom_num] * 0.3
                    else:
                        radius = 0.3
                    atom_radii_list.append(radius)
                except KeyError:
                    default_color_q = CPK_COLORS['DEFAULT']
                    atom_colors_list.append((default_color_q.redF(), default_color_q.greenF(), default_color_q.blueF()))
                    atom_radii_list.append(0.3) 

            glyph_source = pv.PolyData(positions)
            glyph_source['colors'] = np.array(atom_colors_list)
            glyph_source['radii'] = np.array(atom_radii_list)

            sphere_geom = pv.Sphere(radius=1.0, theta_resolution=16, phi_resolution=16)

            glyphs = glyph_source.glyph(
                scale='radii',
                geom=sphere_geom,
                orient=False
            )
            self.plotter.add_mesh(glyphs, scalars='colors', rgb=True, **mesh_props)

        # --- 2. 結合を描画 (Stick スタイル) ---
        try:
            cutoffs = natural_cutoffs(atoms_to_draw)
            neighbor_list = NeighborList(cutoffs, self_interaction=False, bothways=True)
            neighbor_list.update(atoms_to_draw)
            matrix = neighbor_list.get_connectivity_matrix()
            coo = matrix.tocoo()
            bond_radius = 0.10
            bond_resolution = 16
            bond_cylinders = []
            for i, j in zip(coo.row, coo.col):
                if i >= j:
                    continue
                sp = positions[i]
                ep = positions[j]
                d = ep - sp 
                h = np.linalg.norm(d) 
                if h == 0: continue
                mid_point = (sp + ep) / 2
                cyl1 = pv.Cylinder(center=(sp + mid_point) / 2, direction=d, 
                                   radius=bond_radius, height=h/2, 
                                   resolution=bond_resolution)
                cyl2 = pv.Cylinder(center=(mid_point + ep) / 2, direction=d, 
                                   radius=bond_radius, height=h/2, 
                                   resolution=bond_resolution)
                bond_cylinders.append(cyl1)
                bond_cylinders.append(cyl2)
            if bond_cylinders:
                combined_bonds = pv.MultiBlock(bond_cylinders).combine()
                self.plotter.add_mesh(combined_bonds, color='grey', **mesh_props)
        except Exception as e:
            print(f"Failed to draw bonds: {e}")
            pass

        # --- 2.5. 原子インデックスをラベル表示 ---
        # スーパーセル表示時は番号ラベルを消す
        if self.show_atom_indices and len(positions) > 0 and not (show_supercell and (n_a > 1 or n_b > 1 or n_c > 1)):
            for i, pos in enumerate(positions):
                self.plotter.add_point_labels(
                    [pos], [str(i)],
                    point_size=0,
                    font_size=12,
                    text_color='#0066CC',
                    always_visible=True,
                    shape=None
                )

        # --- 3. セル（単位格子）を描画 (手動) ---
        # 通常セルのみ描画（スーパーセル枠は今は描かない）
        if self.atoms.pbc.any():
            cell_matrix = self.atoms.get_cell()
            origin = np.array([0.0, 0.0, 0.0])
            corners = [
                origin,
                origin + cell_matrix[0],
                origin + cell_matrix[1],
                origin + cell_matrix[2],
                origin + cell_matrix[0] + cell_matrix[1],
                origin + cell_matrix[0] + cell_matrix[2],
                origin + cell_matrix[1] + cell_matrix[2],
                origin + cell_matrix[0] + cell_matrix[1] + cell_matrix[2]
            ]
            corners = np.array(corners)
            axis_lines = [
                (0, 1, 'red', 'a'),
                (0, 2, 'green', 'b'),
                (0, 3, 'blue', 'c')
            ]
            for (start_idx, end_idx, color, label) in axis_lines:
                line_segment = np.array([corners[start_idx], corners[end_idx]])
                self.plotter.add_lines(line_segment, color=color, width=5)
                end_point = corners[end_idx]
                self.plotter.add_point_labels(
                    [end_point], [label],
                    point_size=0,
                    font_size=20,
                    text_color=color,
                    bold=True,
                    always_visible=True,
                    shape=None
                )
            other_lines_indices = [
                (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 6), 
                (4, 7), (5, 7), (6, 7)
            ]
            for (start_idx, end_idx) in other_lines_indices:
                line_segment = np.array([corners[start_idx], corners[end_idx]])
                self.plotter.add_lines(line_segment, color='white', width=3) 

        try:
            self.plotter.camera.reset_clipping_range()
        except Exception:
            pass 

        cell_visual_center = cell_center
        if self.atoms.pbc.any():
            cell = self.atoms.get_cell()
            cell_visual_center = (cell[0] + cell[1] + cell[2]) / 2.0
        if force_reset or not self.camera_state:
            self.plotter.reset_camera()
            self.plotter.camera.focal_point = cell_visual_center
            self.camera_state = None 
        else:
            self.plotter.camera = self.camera_state
            self.plotter.camera.focal_point = cell_visual_center

    # --- [変更なし v14] カメラリセット機能
    def reset_camera_view(self):
        """カメラビューをリセットするために、内部状態をクリアして再描画する"""
        if self.atoms is None:
            return
            
        self.camera_state = None 
        
        cell_center = np.array([0.0, 0.0, 0.0])
        self.draw_scene_manually(force_reset=True, cell_center=cell_center)

    # --- [変更なし v16] 座標最適化 (Wrap) 機能 ---
    def optimize_coordinate(self):
        """原子をセル内に折りたたむ (wrap)"""
        if self.atoms is None:
            return
        
        if not self.atoms.pbc.any():
            QMessageBox.warning(self, "Warning", "Cell is not set. Cannot wrap atoms.")
            return
            
        try:
            # wrap() を実行して原子をセル内に移動
            self.atoms.wrap(pbc=self.atoms.pbc)
            
            # 原点基準で再描画
            cell_center = np.array([0.0, 0.0, 0.0])
            self.draw_scene_manually(force_reset=False, cell_center=cell_center)
            
            QMessageBox.information(self, "Success", "Atoms wrapped into cell successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to optimize coordinates:\n{e}")
    
    # --- [追加 v19] 原子インデックス表示切替 ---
    def toggle_atom_indices(self):
        """原子インデックスの表示/非表示を切り替え"""
        if self.atoms is None:
            return
        
        self.show_atom_indices = not self.show_atom_indices
        
        # 原点基準で再描画
        cell_center = np.array([0.0, 0.0, 0.0])
        self.draw_scene_manually(force_reset=False, cell_center=cell_center)
    # --- ここまで ---
    
    # --- [追加 v20] 平行移動機能 ---
    def apply_translation(self):
        """指定された量だけ分子を平行移動（XYZまたはABCモード）"""
        if self.atoms is None:
            return
        
        try:
            if self.translate_xyz_radio.isChecked():
                # XYZモード：デカルト座標系で移動
                translation = np.array([
                    self.translate_inputs['X'].value(),
                    self.translate_inputs['Y'].value(),
                    self.translate_inputs['Z'].value()
                ])
                
                self.atoms.positions += translation
            else:
                # ABCモード：セル軸座標系で移動
                cell = self.atoms.get_cell()
                translation = (
                    self.translate_abc_inputs['a'].value() * cell[0] +
                    self.translate_abc_inputs['b'].value() * cell[1] +
                    self.translate_abc_inputs['c'].value() * cell[2]
                )
                
                self.atoms.positions += translation
            
            # 再描画
            cell_center = np.array([0.0, 0.0, 0.0])
            self.draw_scene_manually(force_reset=False, cell_center=cell_center)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply translation:\n{e}")
    
    # --- [追加 v20] 回転機能 (XYZ/ABCモード対応) ---
    def apply_rotation(self):
        """指定された角度だけ分子を回転（XYZモード: 指定原子中心、ABCモード: 軸上原子基準）"""
        if self.atoms is None:
            return
        
        try:
            if self.rotate_xyz_radio.isChecked():
                # XYZモード：指定原子を中心に回転
                angles = np.array([
                    np.radians(self.rotate_inputs['X'].value()),
                    np.radians(self.rotate_inputs['Y'].value()),
                    np.radians(self.rotate_inputs['Z'].value())
                ])
                
                if np.any(np.abs(angles) > 1e-6):
                    # 回転中心の原子をユーザーに尋ねる
                    atom_idx_str, ok = QInputDialog.getText(
                        self,
                        "Rotation Center",
                        f"Enter atom index for rotation center (0-{len(self.atoms)-1}):",
                        text="0"
                    )
                    
                    if not ok:
                        return
                    
                    try:
                        atom_idx = int(atom_idx_str)
                        if atom_idx < 0 or atom_idx >= len(self.atoms):
                            raise ValueError(f"Atom index must be between 0 and {len(self.atoms)-1}")
                    except ValueError as e:
                        QMessageBox.warning(self, "Input Error", f"Invalid atom index: {e}")
                        return
                    
                    # 指定原子を中心に回転
                    center = self.atoms.positions[atom_idx]
                    self.atoms.positions -= center
                    
                    # オイラー角から回転行列を作成（XYZの順）
                    rotation = Rotation.from_euler('xyz', angles)
                    self.atoms.positions = rotation.apply(self.atoms.positions)
                    
                    self.atoms.positions += center
                    
            else:
                # ABCモード：セル軸周りに回転（軸上の原子を基準）
                if not self.atoms.pbc.any():
                    QMessageBox.warning(self, "Warning", "Cell is not set. Cannot use ABC mode.")
                    return
                
                cell = self.atoms.get_cell()
                
                # 各軸の回転角を取得
                angles_abc = np.array([
                    np.radians(self.rotate_abc_inputs['a'].value()),
                    np.radians(self.rotate_abc_inputs['b'].value()),
                    np.radians(self.rotate_abc_inputs['c'].value())
                ])
                
                # 回転を適用する軸を決定（ゼロでない角度の軸）
                for axis_idx, angle in enumerate(angles_abc):
                    if np.abs(angle) > 1e-6:
                        axis_name = ['a', 'b', 'c'][axis_idx]
                        
                        # セル軸ベクトルを取得
                        cell_vector = cell[axis_idx]
                        axis_direction = cell_vector / np.linalg.norm(cell_vector)
                        
                        # この軸上の原子を検出
                        tolerance = 0.1  # 軸からの許容距離（Å）
                        positions = self.atoms.get_positions()
                        atoms_on_axis = []
                        
                        for atom_idx, pos in enumerate(positions):
                            # 軸方向への射影
                            projection = np.dot(pos, axis_direction) * axis_direction
                            # 軸からの垂直距離
                            perpendicular = pos - projection
                            distance = np.linalg.norm(perpendicular)
                            
                            if distance < tolerance:
                                atoms_on_axis.append(atom_idx)
                        
                        if len(atoms_on_axis) == 0:
                            QMessageBox.warning(
                                self, 
                                "Warning", 
                                f"No atoms found on {axis_name}-axis within {tolerance}Å.\n"
                                f"Cannot determine rotation center."
                            )
                            return
                        
                        # 軸上の原子の重心を回転中心とする
                        axis_positions = positions[atoms_on_axis]
                        axis_centroid = axis_positions.mean(axis=0)
                        
                        # 回転中心の軸方向座標
                        rotation_center_coord = np.dot(axis_centroid, axis_direction)
                        rotation_center = rotation_center_coord * axis_direction
                        
                        # 回転を適用
                        self.atoms.positions -= rotation_center
                        rotation = Rotation.from_rotvec(angle * axis_direction)
                        self.atoms.positions = rotation.apply(self.atoms.positions)
                        self.atoms.positions += rotation_center
            
            # 再描画
            cell_center = np.array([0.0, 0.0, 0.0])
            self.draw_scene_manually(force_reset=False, cell_center=cell_center)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply rotation:\n{e}")
    # --- ここまで ---
    
    # --- [追加 v22] 複数原子固定＆セル内収納機能 ---
    def fix_atom0_and_fit(self):
        """ABC軸のいずれかに乗っている複数原子を自動検出して固定し、軸周りに回転してセル内に収める"""
        if self.atoms is None:
            return
        
        if not self.atoms.pbc.any():
            QMessageBox.warning(self, "Warning", "Cell is not set.")
            return
        
        try:
            # セル情報を取得
            cell = self.atoms.get_cell()
            positions = self.atoms.get_positions()
            
            # 各セル軸について、軸上に乗っている原子を検出
            tolerance = 0.1  # 軸からの許容距離（Å）
            
            axis_candidates = []
            for axis_idx in range(3):
                axis_vector = cell[axis_idx]
                axis_direction = axis_vector / np.linalg.norm(axis_vector)
                
                # 各原子について、軸からの垂直距離を計算
                atoms_on_axis = []
                for atom_idx, pos in enumerate(positions):
                    # 軸方向への射影
                    projection = np.dot(pos, axis_direction) * axis_direction
                    # 軸からの垂直距離
                    perpendicular = pos - projection
                    distance = np.linalg.norm(perpendicular)
                    
                    if distance < tolerance:
                        atoms_on_axis.append(atom_idx)
                
                if len(atoms_on_axis) >= 2:  # 最低2個の原子が軸上にある
                    axis_candidates.append({
                        'axis_idx': axis_idx,
                        'axis_name': ['a-axis', 'b-axis', 'c-axis'][axis_idx],
                        'atoms': atoms_on_axis,
                        'count': len(atoms_on_axis)
                    })
            
            # 軸上の原子が見つからない場合はエラー
            if len(axis_candidates) == 0:
                error_msg = (
                    f"No atoms found on any cell axis within {tolerance}Å tolerance.\n\n"
                    "Please ensure atoms are aligned to one of the cell axes (a, b, or c)\n"
                    "before using this function."
                )
                QMessageBox.critical(self, "Error", error_msg)
                return
            
            # 最も多くの原子が乗っている軸を選択
            best_candidate = max(axis_candidates, key=lambda x: x['count'])
            cell_axis_idx = best_candidate['axis_idx']
            axis_name = best_candidate['axis_name']
            fixed_indices = best_candidate['atoms']
            
            # 確認メッセージ
            atom_list = ', '.join(map(str, fixed_indices[:10]))
            if len(fixed_indices) > 10:
                atom_list += f", ... ({len(fixed_indices)} total)"
            
            reply = QMessageBox.question(
                self,
                "Auto-detected Atoms on Axis",
                f"Detected {len(fixed_indices)} atoms on {axis_name}:\n"
                f"Atom indices: {atom_list}\n\n"
                f"Continue with rotation optimization?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # セル軸ベクトルを設定
            cell_vector = cell[cell_axis_idx]
            target_direction = cell_vector / np.linalg.norm(cell_vector)
            
            # 他の2軸のインデックス
            other_axes = [i for i in range(3) if i != cell_axis_idx]
            
            # 固定原子群の重心を計算（軸方向の座標）
            fixed_positions = self.atoms.positions[fixed_indices]
            fixed_centroid = fixed_positions.mean(axis=0)
            rotation_center_coord = np.dot(fixed_centroid, target_direction)
            rotation_center = rotation_center_coord * target_direction
            
            # 最適な回転角を探索
            best_angle = 0.0
            min_overflow = float('inf')
            
            # 0度から360度まで5度刻みで試行
            for test_angle_deg in range(0, 360, 5):
                test_angle = np.radians(test_angle_deg)
                
                # テスト回転を適用
                test_positions = self.atoms.positions.copy()
                test_positions -= rotation_center
                
                # 軸周りに回転
                test_rotation = Rotation.from_rotvec(test_angle * target_direction)
                test_positions = test_rotation.apply(test_positions)
                test_positions += rotation_center
                
                # 他の2軸方向のはみ出しを計算
                overflow = 0.0
                for other_idx in other_axes:
                    other_vector = cell[other_idx]
                    other_direction = other_vector / np.linalg.norm(other_vector)
                    other_size = np.linalg.norm(other_vector)
                    
                    # この軸方向の座標
                    coords = np.dot(test_positions, other_direction)
                    
                    overflow += max(0, -coords.min())
                    overflow += max(0, coords.max() - other_size)
                
                if overflow < min_overflow:
                    min_overflow = overflow
                    best_angle = test_angle
            
            # 最適な角度で回転を適用
            if abs(best_angle) > 1e-6:
                self.atoms.positions -= rotation_center
                optimal_rotation = Rotation.from_rotvec(best_angle * target_direction)
                self.atoms.positions = optimal_rotation.apply(self.atoms.positions)
                self.atoms.positions += rotation_center
            
            # 軸方向の一番下の原子がセルの下端（0）に来るように平行移動
            final_positions = self.atoms.positions
            axis_coords = np.dot(final_positions, target_direction)
            axis_min = axis_coords.min()
            # 必要な平行移動量（axis_minが0になるように）
            shift_correction = -axis_min * target_direction
            self.atoms.positions += shift_correction
            
            # 再描画
            cell_center = np.array([0.0, 0.0, 0.0])
            self.draw_scene_manually(force_reset=False, cell_center=cell_center)
            
            QMessageBox.information(self, "Success", f"Molecule fitted with {len(fixed_indices)} atoms fixed on {axis_name}.")
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fit molecule:\n{e}")
    # --- ここまで ---
    
    # --- [変更 v19] 分子配置機能 (複数原子指定対応) ---
    def fit_molecule_to_cell(self):
        """複数原子を指定して分子を軸に沿うように配置"""
        if self.atoms is None:
            return
            
        if not self.atoms.pbc.any():
            QMessageBox.warning(self, "Warning", "Cell is not set. Cannot fit molecule.")
            return
        
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTextEdit
        
        # ダイアログを作成
        dialog = QDialog(self)
        dialog.setWindowTitle("Fit Molecule to Axis")
        dialog.resize(450, 350)
        layout = QVBoxLayout(dialog)
        
        # 情報表示
        info_label = QLabel(f"Total atoms: {len(self.atoms)}\nYou can specify multiple atom indices separated by commas")
        layout.addWidget(info_label)
        
        # 配置軸を選択 (abcを先に)
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("Target axis:"))
        axis_combo = QComboBox()
        axis_combo.addItems(['a-axis', 'b-axis', 'c-axis', 'X-axis', 'Y-axis', 'Z-axis'])
        axis_layout.addWidget(axis_combo)
        layout.addLayout(axis_layout)
        
        # 軸方向を決める原子群（カンマ区切り）
        direction_layout = QVBoxLayout()
        direction_layout.addWidget(QLabel("Atom indices to define axis direction (comma-separated):"))
        direction_input = QTextEdit()
        direction_input.setMaximumHeight(60)
        direction_input.setPlaceholderText("e.g., 0,1,2,3")
        direction_layout.addWidget(direction_input)
        layout.addLayout(direction_layout)
        
        # 末端原子インデックス（オプション）
        terminal_layout = QVBoxLayout()
        terminal_layout.addWidget(QLabel("Terminal atom indices (optional, comma-separated):"))
        terminal_input = QTextEdit()
        terminal_input.setMaximumHeight(60)
        terminal_input.setPlaceholderText(f"e.g., {len(self.atoms)-1} or leave empty")
        terminal_layout.addWidget(terminal_input)
        layout.addLayout(terminal_layout)
        
        # セル内での配置位置（分率座標）
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position along axis (0.0-1.0):"))
        position_input = QLineEdit("0.5")
        position_layout.addWidget(position_input)
        layout.addLayout(position_layout)
        
        # [追加 v20] VdW半径による余白設定
        from PyQt6.QtWidgets import QCheckBox
        vdw_margin_layout = QHBoxLayout()
        vdw_margin_checkbox = QCheckBox("Add VdW radius margin at terminals")
        vdw_margin_checkbox.setChecked(True)
        vdw_margin_layout.addWidget(vdw_margin_checkbox)
        layout.addLayout(vdw_margin_layout)
        
        # ボタン
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        try:
            # パラメータを取得
            axis_name = axis_combo.currentText()
            direction_text = direction_input.toPlainText().strip()
            terminal_text = terminal_input.toPlainText().strip()
            target_position = float(position_input.text())
            
            # 入力値の検証
            if target_position < 0.0 or target_position > 1.0:
                raise ValueError("Position must be between 0.0 and 1.0")
            
            # 原子インデックスをパース
            def parse_indices(text):
                if not text:
                    return []
                indices = []
                for item in text.split(','):
                    item = item.strip()
                    if item:
                        idx = int(item)
                        if idx < 0 or idx >= len(self.atoms):
                            raise ValueError(f"Atom index {idx} is out of range (0-{len(self.atoms)-1})")
                        indices.append(idx)
                return indices
            
            direction_indices = parse_indices(direction_text)
            terminal_indices = parse_indices(terminal_text)
            
            if len(direction_indices) < 2:
                raise ValueError("At least 2 atoms are required to define axis direction")
            
            # 現在の原子位置を取得
            positions = self.atoms.get_positions()
            
            # 方向ベクトルを計算（最小二乗法で直線フィッティング）
            direction_positions = positions[direction_indices]
            centroid = direction_positions.mean(axis=0)
            
            # 共分散行列から主軸を計算
            centered = direction_positions - centroid
            cov_matrix = np.cov(centered.T)
            eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
            
            # 最大固有値に対応する固有ベクトルが主軸方向
            principal_axis = eigenvectors[:, np.argmax(eigenvalues)].real
            
            # 末端原子が指定されている場合、方向を調整
            if len(terminal_indices) > 0:
                terminal_positions = positions[terminal_indices]
                terminal_centroid = terminal_positions.mean(axis=0)
                to_terminal = terminal_centroid - centroid
                
                # 主軸の向きを末端方向に合わせる
                if np.dot(principal_axis, to_terminal) < 0:
                    principal_axis = -principal_axis
            else:
                # 末端が指定されていない場合、正の方向（セルに入る向き）に調整
                # 方向原子群の重心から最も遠い原子を末端とみなす
                distances = np.linalg.norm(direction_positions - centroid, axis=1)
                farthest_idx = direction_indices[np.argmax(distances)]
                to_farthest = positions[farthest_idx] - centroid
                
                # 主軸が最も遠い原子に向くように調整
                if np.dot(principal_axis, to_farthest) < 0:
                    principal_axis = -principal_axis
            
            molecule_vector = principal_axis
            
            # 指定原子を軸上に配置するための追加回転を計算
            # （主軸周りの回転で他の2軸成分をゼロにする）
            
            # 目標軸ベクトルを取得
            if axis_name in ['X-axis', 'Y-axis', 'Z-axis']:
                # デカルト座標系の軸
                axis_map = {'X-axis': np.array([1, 0, 0]), 
                           'Y-axis': np.array([0, 1, 0]), 
                           'Z-axis': np.array([0, 0, 1])}
                target_direction = axis_map[axis_name]
            else:
                # セル軸
                axis_map = {'a-axis': 0, 'b-axis': 1, 'c-axis': 2}
                cell = self.atoms.get_cell()
                cell_vector = cell[axis_map[axis_name]]
                target_direction = cell_vector / np.linalg.norm(cell_vector)
            
            # 分子ベクトルをターゲット軸に沿って配置
            # 1. 指定原子群の重心を原点に移動
            direction_positions = self.atoms.get_positions()[direction_indices]
            direction_centroid = direction_positions.mean(axis=0)
            self.atoms.positions -= direction_centroid
            
            # 2. 分子の向きをターゲット軸に合わせる（回転）
            mol_direction = molecule_vector / np.linalg.norm(molecule_vector)
            
            # 回転軸と回転角を計算
            rotation_axis = np.cross(mol_direction, target_direction)
            rotation_axis_norm = np.linalg.norm(rotation_axis)
            
            if rotation_axis_norm > 1e-6:  # ベクトルが平行でない場合
                rotation_axis = rotation_axis / rotation_axis_norm
                rotation_angle = np.arccos(np.clip(np.dot(mol_direction, target_direction), -1.0, 1.0))
                
                # 回転を適用
                rotation = Rotation.from_rotvec(rotation_angle * rotation_axis)
                self.atoms.positions = rotation.apply(self.atoms.positions)
            
            # 3. 指定原子群を目標軸上に正確に配置（軸周りの回転で他の成分をゼロに）
            if axis_name in ['X-axis', 'Y-axis', 'Z-axis']:
                axis_map = {'X-axis': 0, 'Y-axis': 1, 'Z-axis': 2}
                axis_idx = axis_map[axis_name]
                other_axes = [i for i in range(3) if i != axis_idx]
                
                # 回転後の原子位置を取得
                rotated_positions = self.atoms.get_positions()
                direction_positions_rotated = rotated_positions[direction_indices]
                
                # 指定原子の軸方向以外の成分の平均を計算
                mean_perpendicular = direction_positions_rotated.mean(axis=0).copy()
                mean_perpendicular[axis_idx] = 0  # 軸方向成分は無視
                
                # 軸周りの回転角を計算（軸に垂直な成分をゼロにする）
                if np.linalg.norm(mean_perpendicular) > 1e-10:
                    # atan2で正確な角度を計算
                    current_angle = np.arctan2(mean_perpendicular[other_axes[1]], 
                                               mean_perpendicular[other_axes[0]])
                    
                    # 軸周りに回転して垂直成分をゼロに
                    rotation_around_axis = Rotation.from_rotvec(-current_angle * target_direction)
                    self.atoms.positions = rotation_around_axis.apply(self.atoms.positions)
                
                # 最終調整: 指定原子の軸方向以外の成分を**強制的に**ゼロに設定
                final_positions = self.atoms.get_positions()
                direction_final = final_positions[direction_indices]
                
                # 軸方向以外の平均座標を計算
                mean_coords = direction_final.mean(axis=0)
                
                # **全原子を平行移動**して、指定原子群の軸方向以外の座標を完全にゼロに
                for other_axis in other_axes:
                    self.atoms.positions[:, other_axis] -= mean_coords[other_axis]
            
            # 4. VdW半径を考慮した余白追加（オプション）
            if vdw_margin_checkbox.isChecked():
                # 末端原子のVdW半径を取得
                vdw_max_index = len(vdw_radii)
                
                if len(terminal_indices) > 0:
                    terminal_atoms = self.atoms[terminal_indices]
                else:
                    # 末端が指定されていない場合、方向原子を使用
                    terminal_atoms = self.atoms[direction_indices]
                
                max_vdw_radius = 0.0
                for atom_idx in (terminal_indices if len(terminal_indices) > 0 else direction_indices):
                    atom_num = self.atoms[atom_idx].number
                    if atom_num < vdw_max_index and vdw_radii[atom_num] > 0:
                        radius = vdw_radii[atom_num]
                    else:
                        radius = 1.5  # デフォルト値
                    max_vdw_radius = max(max_vdw_radius, radius)
                
                # セルサイズを調整して余白を追加
                current_positions = self.atoms.get_positions()
                
                if axis_name in ['X-axis', 'Y-axis', 'Z-axis']:
                    axis_map = {'X-axis': 0, 'Y-axis': 1, 'Z-axis': 2}
                    axis_idx = axis_map[axis_name]
                    
                    # 軸方向の範囲を計算
                    axis_coords = current_positions[:, axis_idx]
                    min_coord = axis_coords.min()
                    max_coord = axis_coords.max()
                    molecule_length = max_coord - min_coord
                    
                    # 必要なセルサイズ（両端にVdW半径分の余白）
                    required_length = molecule_length + 2 * max_vdw_radius
                    
                    # 現在のセルパラメータを取得
                    cell_params = list(self.atoms.cell.cellpar())
                    cell_params[axis_idx] = required_length
                    
                    # セルを更新
                    from ase.geometry import cellpar_to_cell
                    new_cell = cellpar_to_cell(cell_params)
                    self.atoms.set_cell(new_cell, scale_atoms=False)
                    
                    # GUIのスピンボックスも更新
                    params_dict = {
                        'a': cell_params[0], 'b': cell_params[1], 'c': cell_params[2],
                        'alpha': cell_params[3], 'beta': cell_params[4], 'gamma': cell_params[5]
                    }
                    self._set_spinbox_values(params_dict)
            
            # 5. 軸周りに回転してセル内に収める（指定原子は軸上に固定）
            cell = self.atoms.get_cell()
            
            if axis_name in ['X-axis', 'Y-axis', 'Z-axis']:
                axis_map = {'X-axis': 0, 'Y-axis': 1, 'Z-axis': 2}
                axis_idx = axis_map[axis_name]
                other_axes = [i for i in range(3) if i != axis_idx]
                
                # 指定原子の軸方向の重心を回転の中心とする
                current_positions = self.atoms.get_positions()
                direction_current = current_positions[direction_indices]
                rotation_center_axis = direction_current[:, axis_idx].mean()
                
                # 軸周りに回転して、セルからはみ出す原子を最小化
                best_angle = 0.0
                min_overflow = float('inf')
                
                # 0度から360度まで5度刻みで試行
                for test_angle_deg in range(0, 360, 5):
                    test_angle = np.radians(test_angle_deg)
                    
                    # テスト回転を適用
                    test_positions = current_positions.copy()
                    
                    # 回転中心を原点に移動
                    rotation_center = np.zeros(3)
                    rotation_center[axis_idx] = rotation_center_axis
                    test_positions -= rotation_center
                    
                    # 軸周りに回転
                    test_rotation = Rotation.from_rotvec(test_angle * target_direction)
                    test_positions = test_rotation.apply(test_positions)
                    
                    # 回転中心を戻す
                    test_positions += rotation_center
                    
                    # 軸に垂直な方向のはみ出しを計算
                    overflow = 0.0
                    for other_idx in other_axes:
                        cell_size = np.linalg.norm(cell[other_idx])
                        coords = test_positions[:, other_idx]
                        
                        # セルの範囲は 0 から cell_size
                        overflow += max(0, -coords.min())  # 負の方向のはみ出し
                        overflow += max(0, coords.max() - cell_size)  # 正の方向のはみ出し
                    
                    if overflow < min_overflow:
                        min_overflow = overflow
                        best_angle = test_angle
                
                # 最適な角度で回転を適用
                if abs(best_angle) > 1e-6:
                    rotation_center = np.zeros(3)
                    rotation_center[axis_idx] = rotation_center_axis
                    self.atoms.positions -= rotation_center
                    
                    optimal_rotation = Rotation.from_rotvec(best_angle * target_direction)
                    self.atoms.positions = optimal_rotation.apply(self.atoms.positions)
                    
                    self.atoms.positions += rotation_center
                
                # 6. 軸方向の位置を調整（target_positionに配置）
                current_positions = self.atoms.get_positions()
                direction_current = current_positions[direction_indices]
                current_axis_position = direction_current[:, axis_idx].mean()
                
                # 目標位置を計算（セルサイズ × target_position）
                target_axis_position = target_position * np.linalg.norm(cell[axis_idx])
                
                # 軸方向のみ平行移動
                shift = np.zeros(3)
                shift[axis_idx] = target_axis_position - current_axis_position
                self.atoms.positions += shift
                
                # 軸方向にもセル内に収まるように調整
                final_positions = self.atoms.get_positions()
                axis_coords = final_positions[:, axis_idx]
                axis_min = axis_coords.min()
                axis_max = axis_coords.max()
                cell_axis_size = np.linalg.norm(cell[axis_idx])
                
                # はみ出している場合は中央に配置
                if axis_min < 0 or axis_max > cell_axis_size:
                    molecule_length = axis_max - axis_min
                    # セルの中央に配置
                    center_position = (cell_axis_size - molecule_length) / 2.0
                    axis_shift = center_position - axis_min
                    
                    shift_correction = np.zeros(3)
                    shift_correction[axis_idx] = axis_shift
                    self.atoms.positions += shift_correction
                
            else:  # a-axis, b-axis, c-axis
                axis_map = {'a-axis': 0, 'b-axis': 1, 'c-axis': 2}
                cell_axis_idx = axis_map[axis_name]
                cell_vector = cell[cell_axis_idx]
                cell_direction = cell_vector / np.linalg.norm(cell_vector)
                
                # 指定原子群の重心を計算（回転・配置の基準点）
                current_positions = self.atoms.get_positions()
                direction_current = current_positions[direction_indices]
                direction_centroid = direction_current.mean(axis=0)
                
                # セル軸方向の座標（内積で計算）
                direction_axis_coord = np.dot(direction_centroid, cell_direction)
                rotation_center = direction_axis_coord * cell_direction
                
                # 軸周りに回転して、セルからはみ出す原子を最小化
                best_angle = 0.0
                min_overflow = float('inf')
                
                # 0度から360度まで5度刻みで試行
                for test_angle_deg in range(0, 360, 5):
                    test_angle = np.radians(test_angle_deg)
                    
                    # テスト回転を適用
                    test_positions = current_positions.copy()
                    test_positions -= rotation_center
                    
                    # セル軸周りに回転
                    test_rotation = Rotation.from_rotvec(test_angle * cell_direction)
                    test_positions = test_rotation.apply(test_positions)
                    test_positions += rotation_center
                    
                    # 他の2軸方向のはみ出しを計算
                    overflow = 0.0
                    for check_idx in range(3):
                        if check_idx == cell_axis_idx:
                            continue
                        
                        check_vector = cell[check_idx]
                        check_direction = check_vector / np.linalg.norm(check_vector)
                        check_size = np.linalg.norm(check_vector)
                        
                        # この軸方向の座標
                        coords = np.dot(test_positions, check_direction)
                        
                        overflow += max(0, -coords.min())
                        overflow += max(0, coords.max() - check_size)
                    
                    if overflow < min_overflow:
                        min_overflow = overflow
                        best_angle = test_angle
                
                # 最適な角度で回転を適用
                if abs(best_angle) > 1e-6:
                    self.atoms.positions -= rotation_center
                    optimal_rotation = Rotation.from_rotvec(best_angle * cell_direction)
                    self.atoms.positions = optimal_rotation.apply(self.atoms.positions)
                    self.atoms.positions += rotation_center
                
                # セル軸方向の位置を調整（指定原子群の重心を基準に）
                current_positions = self.atoms.get_positions()
                direction_current = current_positions[direction_indices]
                direction_centroid = direction_current.mean(axis=0)
                current_axis_position = np.dot(direction_centroid, cell_direction)
                
                # 目標位置
                target_axis_position = target_position * np.linalg.norm(cell_vector)
                
                # セル軸方向のみ平行移動
                shift = (target_axis_position - current_axis_position) * cell_direction
                self.atoms.positions += shift
                
                # セル軸方向にもセル内に収まるように調整
                final_positions = self.atoms.get_positions()
                final_axis_coords = np.dot(final_positions, cell_direction)
                axis_min = final_axis_coords.min()
                axis_max = final_axis_coords.max()
                cell_axis_size = np.linalg.norm(cell_vector)
                
                # はみ出している場合は中央に配置
                if axis_min < 0 or axis_max > cell_axis_size:
                    molecule_length = axis_max - axis_min
                    # セルの中央に配置
                    center_position = (cell_axis_size - molecule_length) / 2.0
                    axis_shift = center_position - axis_min
                    
                    shift_correction = axis_shift * cell_direction
                    self.atoms.positions += shift_correction
            
            # 再描画
            cell_center = np.array([0.0, 0.0, 0.0])
            self.draw_scene_manually(force_reset=False, cell_center=cell_center)
            
            margin_msg = "\n(VdW margin added)" if vdw_margin_checkbox.isChecked() else ""
            QMessageBox.information(self, "Success", f"Molecule fitted to {axis_name}.{margin_msg}")
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fit molecule:\n{e}")
    # --- ここまで ---

    def save_cif_file(self):
        if self.atoms is None:
            QMessageBox.warning(self, "Error", "No structure to save.")
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save as CIF",
            "",
            "Crystallographic Information File (*.cif)"
        )
        if file_name:
            try:
                ase.io.write(file_name, self.atoms, format='cif')
                QMessageBox.information(self, "Success", f"File saved successfully:\n{file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

# --- アプリケーションの実行 ---

def run_app():
    """アプリケーションを実行するためのメイン関数"""
    app = QApplication(sys.argv)
    window = CellSetterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()

