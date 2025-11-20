import numpy as np
import scipy.linalg

class Ket:
    def __init__(self, coef):
        self.coef = np.array(coef, dtype=complex)

        # to represent real values as real vector
        t=0
        for a in coef:
            if np.imag(a) == 0:
                t=0
            else:
                t=1
                break
        if t==0:
            self.coef = np.array(coef, dtype=float)
    
    def __add__(self, other):
        if not isinstance(other, Ket):
            raise ValueError("Can only add another Ket.")
        return Ket(self.coef + other.coef)
    
    def __sub__(self, other):
        if not isinstance(other, Ket):
            raise ValueError("Can only subtract another Ket.")
        return Ket(self.coef - other.coef)

    def __mul__(self, scalar):
        return Ket(scalar * self.coef)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __repr__(self):
        return f'Ket({self.coef})'
    
    def dagger(self):
        return Bra(np.conjugate(self.coef))
    
    def inner_product(self, another):
        if not isinstance(another, Bra):
            raise ValueError('Inner Product can only be taken with Bra')
        else:
            return np.dot(self.coef, another.coef)
        
    def outer_product(self, another):
        if not isinstance(another, Bra):
            raise ValueError('Outer Product can only be taken with Bra')
        else:
            return np.outer(self.coef,another.coef)
        
    def tensor(self, *args):
        result = self.coef
        for another in args:
            if not isinstance(another, Ket):
                raise ValueError("Tensor product can only be performed with Kets.")
            result = np.kron(result, another.coef)
        return Ket(result)


    
    
 
class Bra:
    def __init__(self,coef):
        self.coef = np.array(coef, dtype=complex).T

        # to represent real values as real vector
        t=0
        for a in coef:
            if np.imag(a) == 0:
                t=0
            else:
                t=1
                break
        if t==0:
            self.coef = np.array(coef, dtype=float)

    def __add__(self, other):
        if not isinstance(other, Bra):
            raise ValueError("Can only add another Bra.")
        return Bra(self.coef + other.coef)
    
    def __sub__(self, other):
        if not isinstance(other, Bra):
            raise ValueError("Can only subtract another Bra.")
        return Bra(self.coef - other.coef)

    def __mul__(self, scalar):
        return Ket(scalar * self.coef)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __repr__(self):
        return f'Bra({self.coef})'
    
    def dagger(self):
        return Ket(np.conjugate(self.coef))
    
    def inner_product(self, another):
        if not isinstance(another, Ket):
            raise ValueError('Inner Product can only be taken with Ket')
        else:
            return np.dot(self.coef, another.coef)
        
    def outer_product(self, another):
        if not isinstance(another, Ket):
            raise ValueError('Outer Product can only be taken with Ket')
        else:
            return np.outer(self.coef,another.coef)
        
    def tensor(self, *args):
        result = self.coef
        for another in args:
            if not isinstance(another, Bra):
                raise ValueError("Tensor product can only be performed with Bras.")
            result = np.kron(result, another.coef)
        return Bra(result)


class Operator:
    def __init__(self, matrix):
        self.matrix = np.array(matrix)

    def __add__(self, another):
        return Operator(self.matrix + another.matrix)
    
    def __sub__(self, another):
        return Operator(self.matrix - another.matrix)
    
    def __mul__(self, scalar):
        return Operator(scalar * np.array(self.matrix))
    
    def __rmul__(self, scalar):
        return Operator(self.__mul__(scalar))
    
    def __matmul__(self,another):
        return Operator(np.matmul(self.matrix , another.matrix))

    def op(self, another):
        if not isinstance(another,Ket):
            raise ValueError('Cannot Operate')
        else:
            return Ket(self.matrix@another.coef)
        
    def dagger(self):
        return Operator(np.conjugate(self.matrix).T)
    
    def hermitian(self):
        return np.array_equal(self.matrix,self.dagger().matrix)
    
    def antihermitian(self):
        return np.array_equal(self.matrix,-self.dagger().matrix)
    
    def normal(self):
        return np.array_equal(self.matrix@self.dagger().matrix,self.dagger().matrix@self.matrix)
        
    def unitary(self):
        if self.matrix.shape[0]==self.matrix.shape[1]:
            return np.array_equal(np.matmul(self.matrix,self.dagger().matrix),np.identity(np.shape(self.matrix)[0]))
        else:
            raise ValueError("It is not a square Matrix")
        
    def tensor(self, *args):
        result = self.matrix
        for another in args:
            if not isinstance(another, Operator):
                raise ValueError("Tensor product can only be performed with Operators.")
            result = np.kron(result, another.matrix)
        return Operator(result)
        
    def commutator(self, another):
        if not isinstance(another, Operator):
            raise ValueError("Commutator can only be computed with another Operator.")
        return Operator(self.matrix @ another.matrix - another.matrix @ self.matrix)
    
    def anti_commutator(self, another):
        if not isinstance(another, Operator):
            raise ValueError("Anti-commutator can only be computed with another Operator.")
        return Operator(self.matrix @ another.matrix + another.matrix @ self.matrix)
    
    def spectral_decom(self):
        if not np.array_equal(self.matrix, self.dagger().matrix):
            raise ValueError("Not an Hermitian operators.")
        
        eigenvalues, eigenvectors = np.linalg.eigh(self.matrix)
        decomposition = []
        for i in range(len(eigenvalues)):
            eigenvalue = eigenvalues[i]
            eigenvector = eigenvectors[:, i]
            decomposition.append((eigenvalue, eigenvector))
        return decomposition

        
    def __repr__(self):
        return f'Operator({self.matrix})'
    
    def partial_trace(self, keep, dims):
        """
        Partial trace keeping the subsystems listed in `keep`.

        Args:
            keep: int or list/tuple of subsystem indices to keep. The order
                  provided in `keep` is preserved in the returned Operator.
            dims: list/tuple of subsystem dimensions.

        Returns:
            Operator wrapping the reduced density/operator matrix.
        """
        # normalize keep to list
        if isinstance(keep, int):
            keep = [keep]
        keep = list(keep)

        N = len(dims)
        if any((k < 0 or k >= N) for k in keep):
            raise ValueError("keep contains invalid subsystem indices")

        if int(np.prod(dims)) != self.matrix.shape[0]:
            raise ValueError("product of dims must equal matrix dimension")

        rho = np.asarray(self.matrix)

        # indices to trace out
        trace_indices = [i for i in range(N) if i not in keep]

        # Reshape into 2N tensor
        reshaped = rho.reshape([*dims, *dims])

        # Trace out unwanted subsystems (ascending order, adjusting indices)
        removed = 0
        for t in sorted(trace_indices):
            t_adj = t - removed
            axis2 = t_adj + (N - removed)
            reshaped = np.trace(reshaped, axis1=t_adj, axis2=axis2)
            removed += 1

        # If no subsystem kept, return 1x1
        if not keep:
            return Operator(reshaped.reshape((1, 1)))

        # Remaining axes are ordered by ascending subsystem index. If the caller
        # requested a different order, permute the axes to match `keep`.
        kept_sorted = sorted(keep)
        if kept_sorted != keep:
            m = len(keep)
            idx_map = [kept_sorted.index(k) for k in keep]
            perm = idx_map + [i + m for i in idx_map]
            reshaped = np.transpose(reshaped, axes=perm)

        dim_keep = int(np.prod([dims[i] for i in keep]))
        reduced = reshaped.reshape((dim_keep, dim_keep))
        return Operator(reduced)
    
        
    def von_neumann_entropy(self):
        if not np.array_equal(self.matrix, self.dagger().matrix):
            raise ValueError("Von Neumann entropy can only be calculated for Hermitian operators.")

        eigenvalues = np.linalg.eigvalsh(self.matrix)
        eigenvalues = eigenvalues[eigenvalues > 0]
        entropy = -np.sum(eigenvalues * np.log(eigenvalues))
        return entropy
    

    pauli_x = [[0, 1], [1, 0]]
    pauli_y = [[0, -1j], [1j, 0]]
    pauli_z = [[1, 0], [0, -1]]
    identity = [[1, 0], [0, 1]]

    @staticmethod
    def cnot(control, target, no_of_qubits):
        if control < 0 or control >= no_of_qubits or target < 0 or target >= no_of_qubits:
            raise ValueError("Control and target qubit indices must be within the range of the number of qubits.")
        if control == target:
            raise ValueError("Control and target qubit indices must be different.")

        dim = 2 ** no_of_qubits
        cnot_matrix = np.zeros((dim, dim), dtype=complex)
        for i in range(dim):
            binary = format(i, f'0{no_of_qubits}b')
            bits = list(binary)
            if bits[no_of_qubits - 1 - control] == '1':
                bits[no_of_qubits - 1 - target] = '1' if bits[no_of_qubits - 1 - target] == '0' else '0'
            j = int(''.join(bits), 2)
            cnot_matrix[j, i] = 1  
        return Operator(cnot_matrix)
    
    @staticmethod
    def hadamard(qubit, no_of_qubits):
        '''
        qubit: index of the qubit to apply Hadamard gate (0-indexed)
        no_of_qubits: total number of qubits in the system
        '''
        if qubit < 0 or qubit >= no_of_qubits:
            raise ValueError("Qubit index must be within the range of the number of qubits.")

        H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
        result = Operator([[1]])
        for i in range(no_of_qubits):
            if i == qubit:
                result = result.tensor(Operator(H))
            else:
                result = result.tensor(Operator(Operator.identity))
        return result
    
class DensityMatrix(Operator):
    def __init__(self, matrix):
        super().__init__(matrix)
        self.is_valid_density_matrix()

    def is_valid_density_matrix(self):
        # Matrix must be square
        if self.matrix.ndim != 2 or self.matrix.shape[0] != self.matrix.shape[1]:
            raise ValueError("Density matrix must be a square matrix.")

        # Hermitian (allow small numerical tolerance)
        if not np.allclose(self.matrix, self.dagger().matrix, atol=1e-8, rtol=1e-8):
            raise ValueError("Density matrix must be Hermitian.")

        # Trace must be 1 within tolerance
        if not np.isclose(np.trace(self.matrix), 1.0, atol=1e-8, rtol=1e-8):
            raise ValueError("Density matrix must have trace equal to 1.")

        # Eigenvalues must be non-negative up to a small negative tolerance
        eigenvalues = np.linalg.eigvalsh(self.matrix)
        tol = 1e-9
        if np.any(eigenvalues < -tol):
            raise ValueError("Density matrix must be positive semi-definite.")

    
    def fidelity(self, another):
        if not isinstance(another, DensityMatrix):
            raise ValueError("Fidelity can only be calculated with another DensityMatrix.")
        
        sqrt_rho = scipy.linalg.sqrtm(self.matrix)
        product = sqrt_rho @ another.matrix @ sqrt_rho
        sqrt_product = scipy.linalg.sqrtm(product)
        fidelity = np.real_if_close(np.trace(sqrt_product)) ** 2
        return fidelity
    
    
    def evolve(self, operator):
        if not isinstance(operator, Operator):
            raise ValueError("Evolution can only be performed with an Operator.")
        U = operator.matrix
        U_dagger = operator.dagger().matrix
        new_matrix = U @ self.matrix @ U_dagger
        return DensityMatrix(new_matrix)
    def partial_trace(self, keep, dims):
        traced_operator = super().partial_trace(keep, dims)
        return DensityMatrix(traced_operator.matrix)
    
    
class QuantumChannel:
    def __init__(self, kraus_operators):
        '''
        kraus_operators: list of Operator instances representing the Kraus operators of the channel
        '''
        self.kraus_operators = kraus_operators

    def apply(self, density_matrix):
        if not isinstance(density_matrix, DensityMatrix):
            raise ValueError("Quantum channel can only be applied to a DensityMatrix.")
        
        new_matrix = np.zeros_like(density_matrix.matrix, dtype=complex)
        for K in self.kraus_operators:
            new_matrix += K.matrix @ density_matrix.matrix @ K.dagger().matrix
        return DensityMatrix(new_matrix)
    @classmethod
    def amplitude_damping(cls, gamma):
        '''
        gamma: damping probability (0 <= gamma <= 1)
        '''
        K0 = Operator([[1, 0], [0, np.sqrt(1 - gamma)]])
        K1 = Operator([[0, np.sqrt(gamma)], [0, 0]])
        return cls([K0, K1])
    @classmethod
    def depolarizing(cls, p):
        d = 2  # Dimension for a qubit
        K0 = Operator(np.sqrt(1 - p) * np.identity(d))
        K1 = Operator(np.sqrt(p / 3) * np.array([[0, 1], [1, 0]]))  # X
        K2 = Operator(np.sqrt(p / 3) * np.array([[0, -1j], [1j, 0]]))  # Y
        K3 = Operator(np.sqrt(p / 3) * np.array([[1, 0], [0, -1]]))  # Z
        return cls([K0, K1, K2, K3])
    @classmethod
    def phase_damping(cls, gamma):
        K0 = Operator([[1, 0], [0, np.sqrt(1 - gamma)]])
        K1 = Operator([[0, 0], [0, np.sqrt(gamma)]])
        return cls([K0, K1])
    
    @staticmethod
    def quantum_teleportation(initial_state, gamma=0.0):
        """
        General quantum teleportation protocol with noise
        
        Parameters:
        initial_state: Ket object representing the state to teleport
        gamma: amplitude damping probability (0 <= gamma <= 1)
        
        Returns:
        Dictionary containing all results and parameters
        """
        
        print("=== QUANTUM TELEPORTATION PROTOCOL ===")
        print(f"Initial state: {initial_state.coef}")
        print(f"Noise parameter gamma: {gamma}")
        
        # Store the original state for fidelity calculation
        rho_target = DensityMatrix(initial_state.outer_product(initial_state.dagger()))
        
        # Define Bell State |Φ+> = (|00> + |11>)/√2
        bell_state = (Ket([1,0,0,0]) + Ket([0,0,0,1])) * (1/np.sqrt(2))
        rho_bell = DensityMatrix(bell_state.outer_product(bell_state.dagger()))
        
        # Combined initial state: |ψ> ⊗ |Φ+>
        psi_combined = initial_state.tensor(bell_state)
        rho_combined = DensityMatrix(psi_combined.outer_product(psi_combined.dagger()))
        
        # Apply amplitude damping channel if gamma > 0
        if gamma > 0:
            K0 = Operator([[1, 0], [0, np.sqrt(1 - gamma)]])
            K1 = Operator([[0, np.sqrt(gamma)], [0, 0]])
            
            # Kraus operators for last two qubits
            M0 = Operator(Operator.identity).tensor(K0, K0)
            M1 = Operator(Operator.identity).tensor(K0, K1)
            M2 = Operator(Operator.identity).tensor(K1, K0)
            M3 = Operator(Operator.identity).tensor(K1, K1)
            krauss_3qubit = [M0, M1, M2, M3]
            
            channel_3qubit = QuantumChannel(krauss_3qubit)
            rho_damped = channel_3qubit.apply(rho_combined)
        else:
            rho_damped = rho_combined
        
        # Apply teleportation operations
        CNot = Operator.cnot(0, 1, 3)  # Control on qubit 0, target on qubit 1
        Hadamard = Operator.hadamard(0, 3)  # Hadamard on qubit 0
        state_after_ops = rho_damped.evolve(CNot).evolve(Hadamard)
        
        # Measurement on first two qubits
        P0 = Operator([[1, 0], [0, 0]])
        P1 = Operator([[0, 0], [0, 1]])
        
        M00 = P0.tensor(P0, Operator(Operator.identity))
        M01 = P0.tensor(P1, Operator(Operator.identity))
        M10 = P1.tensor(P0, Operator(Operator.identity))
        M11 = P1.tensor(P1, Operator(Operator.identity))
        
        # Calculate measurement probabilities
        prob_00 = np.real_if_close(np.trace(M00.matrix @ state_after_ops.matrix))
        prob_01 = np.real_if_close(np.trace(M01.matrix @ state_after_ops.matrix))
        prob_10 = np.real_if_close(np.trace(M10.matrix @ state_after_ops.matrix))
        prob_11 = np.real_if_close(np.trace(M11.matrix @ state_after_ops.matrix))
        
        # Ensure probabilities are positive and normalized
        probs = [max(0, p) for p in [prob_00, prob_01, prob_10, prob_11]]
        total_prob = sum(probs)
        if total_prob > 0:
            prob_00, prob_01, prob_10, prob_11 = [p/total_prob for p in probs]
        
        print(f"\nMeasurement probabilities:")
        print(f"P(|00⟩) = {prob_00:.4f}")
        print(f"P(|01⟩) = {prob_01:.4f}")
        print(f"P(|10⟩) = {prob_10:.4f}")
        print(f"P(|11⟩) = {prob_11:.4f}")
        
        # Apply corrections and calculate fidelity
        X_gate = Operator(Operator.pauli_x)
        Z_gate = Operator(Operator.pauli_z)
        
        correction_gates = {
            '00': Operator(Operator.identity),
            '01': X_gate,
            '10': Z_gate,
            '11': X_gate @ Z_gate
        }
        
        fidelities = {}
        post_measurement_states = {}
        
        for outcome, prob in [('00', prob_00), ('01', prob_01), ('10', prob_10), ('11', prob_11)]:
            if prob > 1e-10:
                M_op = locals()[f"M{outcome}"]
                # Post-measurement state
                rho_post = DensityMatrix((M_op.matrix @ state_after_ops.matrix @ M_op.matrix) / prob)
                
                # Get third qubit state (teleported qubit)
                rho_third = rho_post.partial_trace(keep=[2], dims=[2, 2, 2])
                
                # Apply correction
                correction = correction_gates[outcome]
                rho_corrected = rho_third.evolve(correction)
                
                # Calculate fidelity
                fidelity = rho_corrected.fidelity(rho_target)
                fidelities[outcome] = fidelity
                post_measurement_states[outcome] = rho_corrected
                
                print(f"\nOutcome {outcome}:")
                print(f"Correction applied: {correction.matrix}")
                print(f"Teleported state:\n{rho_corrected.matrix}")
                print(f"Fidelity with original: {fidelity:.6f}")
        
        # Calculate average fidelity
        avg_fidelity = sum(fidelities[outcome] * prob for outcome, prob in 
                        [('00', prob_00), ('01', prob_01), ('10', prob_10), ('11', prob_11)]
                        if outcome in fidelities)
        
        print(f"\n=== RESULTS SUMMARY ===")
        print(f"Average fidelity: {avg_fidelity:.6f}")
        
        # Return all results
        return {
            'initial_state': initial_state,
            'gamma': gamma,
            'measurement_probabilities': {
                '00': prob_00, '01': prob_01, '10': prob_10, '11': prob_11
            },
            'fidelities': fidelities,
            'average_fidelity': avg_fidelity,
            'post_measurement_states': post_measurement_states
        }
    


    




